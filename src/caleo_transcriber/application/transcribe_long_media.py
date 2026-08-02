"""Orquestra mídia longa com uploads sequenciais e retomada segura."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock

from caleo_transcriber.application.checkpoints import (
    CheckpointChunk,
    CheckpointStore,
    ChunkCheckpointState,
    LongMediaCheckpoint,
)
from caleo_transcriber.application.media import (
    AudioChunkExtractor,
    AudioExtractor,
    MediaError,
    MediaFailure,
    MediaProbe,
    PreparedAudio,
    PreparedAudioLease,
    SilenceDetector,
)
from caleo_transcriber.application.output import (
    OutputFormat,
    OutputWriteCancelled,
    OutputWriteError,
    TranscriptOutputWriter,
)
from caleo_transcriber.application.transcribe_single_file import (
    AttemptEvent,
    AttemptEvents,
    AttemptFailure,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
    TranscribeSingleFileSuccess,
    TranscriptionAlreadyRunningError,
)
from caleo_transcriber.application.transcription import (
    ProviderFailure,
    TranscriptionFailure,
    TranscriptionProvider,
    TranscriptionRequest,
    TranscriptionSegment,
    TranscriptionSuccess,
)
from caleo_transcriber.domain import AttemptState
from caleo_transcriber.domain.long_media import (
    OVERLAP_MS,
    ChunkPlan,
    ChunkTranscript,
    TimedText,
    merge_transcripts,
    plan_chunks,
)


@dataclass(frozen=True, slots=True)
class TranscribeLongMediaCommand:
    attempt_id: str
    source: Path
    output_directory: Path
    workspace: Path
    output_format: OutputFormat = OutputFormat.TXT
    language: str | None = None
    retry_failed: bool = False
    confirm_ambiguous: bool = False
    output_name_suffix: str = ""


class TranscribeLongMedia:
    """Caso de uso sem dependência de framework ou adapter concreto."""

    def __init__(
        self,
        media_probe: MediaProbe,
        audio_extractor: AudioExtractor,
        chunk_extractor: AudioChunkExtractor,
        silence_detector: SilenceDetector,
        provider: TranscriptionProvider,
        checkpoint_store: CheckpointStore,
        output_writer: TranscriptOutputWriter,
        events: AttemptEvents,
        source_fingerprint: Callable[[Path], str],
        parameter_hash: Callable[[Mapping[str, object]], str],
        clock: Callable[[], datetime],
    ) -> None:
        self._media_probe = media_probe
        self._audio_extractor = audio_extractor
        self._chunk_extractor = chunk_extractor
        self._silence_detector = silence_detector
        self._provider = provider
        self._checkpoints = checkpoint_store
        self._output_writer = output_writer
        self._events = events
        self._source_fingerprint = source_fingerprint
        self._parameter_hash = parameter_hash
        self._clock = clock
        self._active = Lock()

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        if not self._active.acquire(blocking=False):
            raise TranscriptionAlreadyRunningError
        try:
            return self._execute(command, should_cancel or (lambda: False))
        finally:
            self._active.release()

    def _execute(
        self,
        command: TranscribeLongMediaCommand,
        cancel: Callable[[], bool],
    ) -> TranscribeSingleFileResult:
        state = AttemptState.READY
        checkpoint_id: str | None = None
        self._publish(command.attempt_id, state)
        state = AttemptState.PREPARING
        self._publish(command.attempt_id, state)
        try:
            if cancel():
                return self._cancel(command, state)
            info = self._media_probe.probe(command.source)
            fingerprint = self._source_fingerprint(command.source)
            parameters_hash = self._parameter_hash(
                {
                    "language": command.language,
                    "model": "whisper-1",
                    "output_format": command.output_format.value,
                    "schema": 1,
                }
            )
            with self._audio_extractor.prepare(
                command.source, info, command.workspace, cancel
            ) as prepared_lease:
                prepared = prepared_lease.audio
                silence_points = (
                    self._silence_detector.detect(prepared.path, cancel)
                    if prepared.size_bytes >= 24_000_000
                    else ()
                )
                plan = list(
                    plan_chunks(
                        duration_ms=round(prepared.duration_seconds * 1000),
                        prepared_bytes=prepared.size_bytes,
                        silence_points_ms=silence_points,
                    )
                )
                checkpoint = self._load_or_create(
                    command, fingerprint, parameters_hash, tuple(plan)
                )
                checkpoint_id = checkpoint.attempt_id
                if (
                    any(
                        chunk.state is ChunkCheckpointState.AMBIGUOUS for chunk in checkpoint.chunks
                    )
                    and not command.confirm_ambiguous
                ):
                    return self._fail(
                        command.attempt_id,
                        state,
                        AttemptFailure.AMBIGUOUS,
                        False,
                        "transcription.error.ambiguous",
                        "CHECKPOINT_AMBIGUOUS",
                    )
                checkpoint = self._reset_explicit_retries(checkpoint, command)
                self._checkpoints.save(checkpoint)
                state = AttemptState.TRANSCRIBING
                self._publish(command.attempt_id, state, total=len(plan))
                transcripts, checkpoint, plan = self._transcribe_chunks(
                    command,
                    prepared,
                    plan,
                    checkpoint,
                    cancel,
                )
                if isinstance(transcripts, TranscribeSingleFileFailure):
                    return transcripts
                if cancel():
                    return self._cancel(command, state, checkpoint.attempt_id)
                consolidated = merge_transcripts(transcripts)
                state = AttemptState.SAVING
                self._publish(command.attempt_id, state, completed=len(plan), total=len(plan))
                try:
                    output = self._output_writer.write_transcript(
                        command.output_directory,
                        _output_source_name(command.source, command.output_name_suffix),
                        consolidated,
                        command.output_format,
                        cancel,
                    )
                except OutputWriteCancelled:
                    return self._cancel(command, state, checkpoint.attempt_id)
                except (OutputWriteError, ValueError):
                    return self._fail(
                        command.attempt_id,
                        state,
                        AttemptFailure.OUTPUT,
                        True,
                        "transcription.error.output",
                        "OUTPUT_WRITE",
                    )
            self._checkpoints.delete(checkpoint.attempt_id)
            state = AttemptState.COMPLETED
            warnings = tuple(
                dict.fromkeys(
                    warning
                    for transcript in transcripts
                    for warning in _warnings_from_chunk(transcript)
                )
            )
            self._publish(
                command.attempt_id,
                state,
                warnings=warnings,
                completed=len(plan),
                total=len(plan),
            )
            return TranscribeSingleFileSuccess(command.attempt_id, output, warnings, state)
        except MediaError as error:
            if error.reason is MediaFailure.CANCELLED:
                return self._cancel(command, state, checkpoint_id)
            return self._fail(
                command.attempt_id,
                state,
                AttemptFailure.INVALID_INPUT
                if error.reason
                in {
                    MediaFailure.MISSING,
                    MediaFailure.EMPTY,
                    MediaFailure.CORRUPT,
                    MediaFailure.NO_AUDIO,
                    MediaFailure.INVALID_DURATION,
                    MediaFailure.UNSUPPORTED,
                }
                else AttemptFailure.PROVIDER,
                error.reason in {MediaFailure.TIMEOUT, MediaFailure.PROCESSING},
                "transcription.error.media",
                f"MEDIA_{error.reason.value.upper()}",
            )

    def _transcribe_chunks(
        self,
        command: TranscribeLongMediaCommand,
        prepared: PreparedAudio,
        plan: list[ChunkPlan],
        checkpoint: LongMediaCheckpoint,
        cancel: Callable[[], bool],
    ) -> (
        tuple[list[ChunkTranscript], LongMediaCheckpoint, list[ChunkPlan]]
        | tuple[TranscribeSingleFileFailure, LongMediaCheckpoint, list[ChunkPlan]]
    ):
        transcripts: list[ChunkTranscript] = []
        index = 0
        while index < len(plan):
            if cancel():
                return (
                    self._cancel(command, AttemptState.TRANSCRIBING, checkpoint.attempt_id),
                    checkpoint,
                    plan,
                )
            chunk = checkpoint.chunks[index]
            chunk_plan = plan[index]
            if chunk.state is ChunkCheckpointState.CONFIRMED:
                success = _deserialize_success(
                    self._checkpoints.load_result(checkpoint.attempt_id, index)
                )
            elif chunk.state is ChunkCheckpointState.FAILED:
                return (
                    self._fail(
                        command.attempt_id,
                        AttemptState.TRANSCRIBING,
                        AttemptFailure.PROVIDER,
                        True,
                        "transcription.error.provider",
                        "CHECKPOINT_FAILED",
                    ),
                    checkpoint,
                    plan,
                )
            else:
                try:
                    lease = self._lease_for_chunk(prepared, chunk_plan, command.workspace, cancel)
                    with lease:
                        checkpoint = _update_chunk(
                            checkpoint,
                            index,
                            state=ChunkCheckpointState.UPLOADING,
                            attempts=chunk.attempts + 1,
                        )
                        self._checkpoints.save(checkpoint)
                        audio = lease.audio
                        result = self._provider.transcribe(
                            TranscriptionRequest(
                                command.attempt_id,
                                audio.path,
                                audio.media_type,
                                audio.size_bytes,
                                command.language,
                            ),
                            cancel,
                        )
                except MediaError as error:
                    if error.reason is MediaFailure.PROVIDER_LIMIT:
                        plan = _split_oversized_plan(plan, index)
                        checkpoint = _replan_checkpoint(checkpoint, plan, index)
                        self._checkpoints.save(checkpoint)
                        continue
                    raise
                if isinstance(result, TranscriptionFailure):
                    if result.category is ProviderFailure.CANCELLED:
                        return (
                            self._cancel(command, AttemptState.TRANSCRIBING, checkpoint.attempt_id),
                            checkpoint,
                            plan,
                        )
                    checkpoint = _update_chunk(checkpoint, index, state=ChunkCheckpointState.FAILED)
                    self._checkpoints.save(checkpoint)
                    return (
                        self._fail(
                            command.attempt_id,
                            AttemptState.TRANSCRIBING,
                            _provider_category(result.category),
                            result.retryable,
                            result.user_message_key,
                            result.diagnostic_code,
                        ),
                        checkpoint,
                        plan,
                    )
                success = result
                result_ref = self._checkpoints.save_result(
                    checkpoint.attempt_id, index, _serialize_success(success)
                )
                checkpoint = _update_chunk(
                    checkpoint,
                    index,
                    state=ChunkCheckpointState.CONFIRMED,
                    result_ref=result_ref,
                )
                self._checkpoints.save(checkpoint)
            transcripts.append(_to_chunk_transcript(chunk_plan, success))
            index += 1
            self._publish(
                command.attempt_id,
                AttemptState.TRANSCRIBING,
                completed=index,
                total=len(plan),
                active=index if index < len(plan) else None,
            )
        return transcripts, checkpoint, plan

    def _lease_for_chunk(
        self,
        prepared: PreparedAudio,
        chunk: ChunkPlan,
        workspace: Path,
        cancel: Callable[[], bool],
    ) -> PreparedAudioLease:
        if chunk.start_ms == 0 and chunk.end_ms == round(prepared.duration_seconds * 1000):
            return _BorrowedPreparedAudioLease(prepared)
        return self._chunk_extractor.prepare_chunk(
            prepared.path, chunk.start_ms, chunk.end_ms, workspace, cancel
        )

    def _load_or_create(
        self,
        command: TranscribeLongMediaCommand,
        fingerprint: str,
        parameters_hash: str,
        plan: tuple[ChunkPlan, ...],
    ) -> LongMediaCheckpoint:
        now = self._clock()
        existing = self._checkpoints.load_matching(fingerprint, parameters_hash, now)
        expected = tuple((item.start_ms, item.end_ms) for item in plan)
        if existing is not None:
            actual = tuple((item.start_ms, item.end_ms) for item in existing.chunks)
            if actual == expected:
                return existing
            self._checkpoints.delete(existing.attempt_id)
        checkpoint = LongMediaCheckpoint(
            attempt_id=command.attempt_id,
            source_fingerprint=fingerprint,
            parameters_hash=parameters_hash,
            created_at=now,
            expires_at=now + timedelta(days=7),
            chunks=tuple(
                CheckpointChunk(item.id, item.start_ms, item.end_ms, ChunkCheckpointState.PENDING)
                for item in plan
            ),
        )
        self._checkpoints.save(checkpoint)
        return checkpoint

    @staticmethod
    def _reset_explicit_retries(
        checkpoint: LongMediaCheckpoint, command: TranscribeLongMediaCommand
    ) -> LongMediaCheckpoint:
        chunks = tuple(
            replace(chunk, state=ChunkCheckpointState.PENDING)
            if (command.retry_failed and chunk.state is ChunkCheckpointState.FAILED)
            or (command.confirm_ambiguous and chunk.state is ChunkCheckpointState.AMBIGUOUS)
            else chunk
            for chunk in checkpoint.chunks
        )
        return replace(checkpoint, chunks=chunks)

    def _cancel(
        self,
        command: TranscribeLongMediaCommand,
        current: AttemptState,
        checkpoint_id: str | None = None,
    ) -> TranscribeSingleFileFailure:
        self._checkpoints.delete(checkpoint_id or command.attempt_id)
        self._publish(command.attempt_id, AttemptState.CANCELLING)
        self._publish(command.attempt_id, AttemptState.CANCELLED, failure=AttemptFailure.CANCELLED)
        return TranscribeSingleFileFailure(
            command.attempt_id,
            AttemptFailure.CANCELLED,
            False,
            "transcription.error.cancelled",
            "ATTEMPT_CANCELLED",
            AttemptState.CANCELLED,
        )

    def _fail(
        self,
        attempt_id: str,
        current: AttemptState,
        category: AttemptFailure,
        retryable: bool,
        user_message_key: str,
        diagnostic_code: str,
    ) -> TranscribeSingleFileFailure:
        _ = current
        self._publish(attempt_id, AttemptState.FAILED, failure=category)
        return TranscribeSingleFileFailure(
            attempt_id,
            category,
            retryable,
            user_message_key,
            diagnostic_code,
            AttemptState.FAILED,
        )

    def _publish(
        self,
        attempt_id: str,
        state: AttemptState,
        failure: AttemptFailure | None = None,
        warnings: tuple[str, ...] = (),
        completed: int = 0,
        total: int | None = None,
        active: int | None = None,
    ) -> None:
        self._events.publish(
            AttemptEvent(attempt_id, state, failure, warnings, completed, total, active)
        )


def _output_source_name(source: Path, suffix: str) -> str:
    """Preserva a extensão da entrada enquanto permite nomes de saída explícitos."""
    if not suffix:
        return source.name
    return f"{source.stem}{suffix}{source.suffix}"


class _BorrowedPreparedAudioLease:
    def __init__(self, audio: PreparedAudio) -> None:
        self._audio = audio

    @property
    def audio(self) -> PreparedAudio:
        return self._audio

    def __enter__(self) -> _BorrowedPreparedAudioLease:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _update_chunk(
    checkpoint: LongMediaCheckpoint,
    index: int,
    *,
    state: ChunkCheckpointState,
    attempts: int | None = None,
    result_ref: str | None = None,
) -> LongMediaCheckpoint:
    chunks = list(checkpoint.chunks)
    old = chunks[index]
    chunks[index] = replace(
        old,
        state=state,
        attempts=old.attempts if attempts is None else attempts,
        result_ref=result_ref,
    )
    return replace(checkpoint, chunks=tuple(chunks))


def _split_oversized_plan(plan: Sequence[ChunkPlan], index: int) -> list[ChunkPlan]:
    oversized = plan[index]
    midpoint = (oversized.start_ms + oversized.end_ms) // 2
    if midpoint - oversized.start_ms <= OVERLAP_MS:
        raise MediaError(MediaFailure.PROVIDER_LIMIT)
    raw = [*plan[:index]]
    raw.extend(
        [
            ChunkPlan(index, oversized.start_ms, midpoint),
            ChunkPlan(index + 1, midpoint - OVERLAP_MS, oversized.end_ms),
        ]
    )
    raw.extend(plan[index + 1 :])
    return [ChunkPlan(new_id, item.start_ms, item.end_ms) for new_id, item in enumerate(raw)]


def _replan_checkpoint(
    checkpoint: LongMediaCheckpoint, plan: Sequence[ChunkPlan], preserve_before: int
) -> LongMediaCheckpoint:
    chunks = tuple(
        checkpoint.chunks[item.id]
        if item.id < preserve_before
        else CheckpointChunk(item.id, item.start_ms, item.end_ms, ChunkCheckpointState.PENDING)
        for item in plan
    )
    return replace(checkpoint, chunks=chunks)


def _to_chunk_transcript(plan: ChunkPlan, success: TranscriptionSuccess) -> ChunkTranscript:
    duration = plan.end_ms - plan.start_ms
    source_segments = success.segments
    if not source_segments and success.text.strip():
        source_segments = (TranscriptionSegment(0, duration, success.text),)
    segments: list[TimedText] = []
    for segment in source_segments:
        start = min(segment.start_ms, max(0, duration - 1))
        end = min(max(start + 1, segment.end_ms), duration)
        if end > start:
            segments.append(TimedText(start, end, segment.text))
    return ChunkTranscript(plan, tuple(segments))


def _serialize_success(success: TranscriptionSuccess) -> bytes:
    payload = {
        "text": success.text,
        "language": success.detected_language,
        "duration_ms": success.duration_ms,
        "warnings": list(success.warnings),
        "segments": [
            {"start_ms": item.start_ms, "end_ms": item.end_ms, "text": item.text}
            for item in success.segments
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _deserialize_success(payload: bytes) -> TranscriptionSuccess:
    value = json.loads(payload.decode("utf-8"))
    return TranscriptionSuccess(
        text=str(value["text"]),
        detected_language=None if value["language"] is None else str(value["language"]),
        duration_ms=int(value["duration_ms"]),
        segments=tuple(
            TranscriptionSegment(int(item["start_ms"]), int(item["end_ms"]), str(item["text"]))
            for item in value["segments"]
        ),
        warnings=tuple(str(item) for item in value["warnings"]),
    )


def _warnings_from_chunk(chunk: ChunkTranscript) -> tuple[str, ...]:
    return ("no_speech_detected",) if not chunk.segments else ()


def _provider_category(reason: ProviderFailure) -> AttemptFailure:
    return {
        ProviderFailure.CREDENTIAL: AttemptFailure.CREDENTIAL,
        ProviderFailure.NETWORK: AttemptFailure.NETWORK,
        ProviderFailure.RATE_LIMIT: AttemptFailure.RATE_LIMIT,
        ProviderFailure.PROVIDER: AttemptFailure.PROVIDER,
        ProviderFailure.PROVIDER_LIMIT: AttemptFailure.PROVIDER,
        ProviderFailure.CANCELLED: AttemptFailure.CANCELLED,
    }[reason]
