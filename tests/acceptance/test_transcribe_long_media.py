from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest
from tests.fakes.transcription_workflow import (
    FakeAudioExtractor,
    FakeMediaProbe,
    FakePreparedAudioLease,
    FakeTranscriptionProvider,
    RecordingAttemptEvents,
)

from caleo_transcriber.application import (
    AttemptFailure,
    CheckpointChunk,
    ChunkCheckpointState,
    LongMediaCheckpoint,
    MediaInfo,
    OutputFormat,
    PreparedAudio,
    ProviderFailure,
    TranscribeLongMedia,
    TranscribeLongMediaCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileSuccess,
    TranscriptionFailure,
    TranscriptionSegment,
    TranscriptionSuccess,
)
from caleo_transcriber.domain import TimedText

pytestmark = pytest.mark.acceptance
ATTEMPT = "12345678-1234-1234-1234-123456789abc"


class FakeChunkExtractor:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    def prepare_chunk(
        self,
        source: Path,
        start_ms: int,
        end_ms: int,
        workspace: Path,
        should_cancel: Callable[[], bool] | None = None,
    ) -> FakePreparedAudioLease:
        self.calls.append((start_ms, end_ms))
        return FakePreparedAudioLease(
            PreparedAudio(
                Path(f"C:/temp/chunk-{len(self.calls)}.mp3"), (end_ms - start_ms) / 1000, 10
            )
        )


class FakeSilenceDetector:
    def __init__(self, points: tuple[int, ...] = ()) -> None:
        self.points = points
        self.calls = 0

    def detect(
        self, source: Path, should_cancel: Callable[[], bool] | None = None
    ) -> tuple[int, ...]:
        self.calls += 1
        return self.points


class MemoryCheckpointStore:
    def __init__(self) -> None:
        self.checkpoint: LongMediaCheckpoint | None = None
        self.results: dict[tuple[str, int], bytes] = {}
        self.deleted: list[str] = []

    def save(self, checkpoint: LongMediaCheckpoint) -> None:
        self.checkpoint = checkpoint

    def load_matching(
        self, source_fingerprint: str, parameters_hash: str, now: datetime
    ) -> LongMediaCheckpoint | None:
        current = self.checkpoint
        if current is None or current.expires_at <= now:
            return None
        if (
            current.source_fingerprint == source_fingerprint
            and current.parameters_hash == parameters_hash
        ):
            return current
        return None

    def save_result(self, attempt_id: str, chunk_id: int, payload: bytes) -> str:
        self.results[(attempt_id, chunk_id)] = payload
        return f"chunk-{chunk_id}.dpapi"

    def load_result(self, attempt_id: str, chunk_id: int) -> bytes:
        return self.results[(attempt_id, chunk_id)]

    def delete(self, attempt_id: str) -> None:
        self.deleted.append(attempt_id)
        if self.checkpoint is not None and self.checkpoint.attempt_id == attempt_id:
            self.checkpoint = None

    def cleanup(self, now: datetime) -> None:
        return None


class RecordingTranscriptWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[TimedText, ...], OutputFormat]] = []
        self.source_names: list[str] = []
        self.output_directories: list[Path] = []

    def write_transcript(
        self,
        output_directory: Path,
        source_name: str,
        segments: tuple[TimedText, ...],
        output_format: OutputFormat,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path:
        self.source_names.append(source_name)
        self.output_directories.append(output_directory)
        self.calls.append((segments, output_format))
        return output_directory / f"result.{output_format.value}"


def _success(text: str, duration: int = 4_000) -> TranscriptionSuccess:
    return TranscriptionSuccess(
        text,
        "pt",
        duration,
        (TranscriptionSegment(0, duration, text),) if text else (),
        warnings=("no_speech_detected",) if not text else (),
    )


def _command(**changes: object) -> TranscribeLongMediaCommand:
    values: dict[str, object] = {
        "attempt_id": ATTEMPT,
        "source": Path("C:/private/video.mp4"),
        "output_directory": Path("C:/output"),
        "workspace": Path("C:/cache"),
        "output_format": OutputFormat.SRT,
    }
    values.update(changes)
    return TranscribeLongMediaCommand(**values)  # type: ignore[arg-type]


def _workflow(
    responses: list[TranscriptionSuccess | TranscriptionFailure],
    store: MemoryCheckpointStore | None = None,
) -> tuple[
    TranscribeLongMedia,
    FakeTranscriptionProvider,
    FakeChunkExtractor,
    MemoryCheckpointStore,
    RecordingTranscriptWriter,
    RecordingAttemptEvents,
]:
    checkpoint_store = store or MemoryCheckpointStore()
    prepared = PreparedAudio(Path("C:/temp/prepared.mp3"), 6.0, 30_000_000)
    provider = FakeTranscriptionProvider(responses)
    chunks = FakeChunkExtractor()
    writer = RecordingTranscriptWriter()
    events = RecordingAttemptEvents()
    use_case = TranscribeLongMedia(
        FakeMediaProbe(MediaInfo(6.0, "mp4", True, True)),
        FakeAudioExtractor(FakePreparedAudioLease(prepared)),
        chunks,
        FakeSilenceDetector(),
        provider,
        checkpoint_store,
        writer,
        events,
        lambda _: "a" * 64,
        lambda _: "b" * 64,
        lambda: datetime(2026, 7, 31, tzinfo=UTC),
    )
    return use_case, provider, chunks, checkpoint_store, writer, events


def test_segmented_flow_is_sequential_merges_overlap_and_cleans_checkpoint() -> None:
    use_case, provider, chunks, store, writer, events = _workflow(
        [_success("zero um dois três"), _success("um dois três quatro")]
    )

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileSuccess)
    assert len(provider.calls) == 2
    assert chunks.calls == [(0, 4_000), (2_000, 6_000)]
    assert [item.text for item in writer.calls[0][0]] == ["zero um dois três", "quatro"]
    assert writer.calls[0][1] is OutputFormat.SRT
    assert store.checkpoint is None
    assert events.events[-1].completed_chunks == 2
    assert events.events[-1].total_chunks == 2


def test_source_folder_name_suffix_is_applied_before_atomic_writer() -> None:
    use_case, _, _, _, writer, _ = _workflow([_success("fala"), _success("continua")])

    result = use_case.execute(
        _command(
            source=Path("C:/private/Demo.mp4"),
            output_directory=Path("C:/private"),
            output_name_suffix="_transcription",
        )
    )

    assert isinstance(result, TranscribeSingleFileSuccess)
    assert writer.source_names == ["Demo_transcription.mp4"]
    assert writer.output_directories == [Path("C:/private")]


def test_failure_preserves_confirmed_chunk_and_retry_sends_only_failed() -> None:
    failure = TranscriptionFailure(ProviderFailure.NETWORK, True, "safe", "NETWORK")
    use_case, first_provider, _, store, _, _ = _workflow([_success("primeiro"), failure])

    first = use_case.execute(_command())
    assert isinstance(first, TranscribeSingleFileFailure)
    assert store.checkpoint is not None
    assert [chunk.state for chunk in store.checkpoint.chunks] == [
        ChunkCheckpointState.CONFIRMED,
        ChunkCheckpointState.FAILED,
    ]

    retry, retry_provider, _, _, writer, _ = _workflow([_success("segundo")], store)
    second = retry.execute(_command(retry_failed=True))

    assert isinstance(second, TranscribeSingleFileSuccess)
    assert len(first_provider.calls) == 2
    assert len(retry_provider.calls) == 1
    assert [item.text for item in writer.calls[0][0]] == ["primeiro", "segundo"]


def test_ambiguous_chunk_requires_confirmation_before_new_upload() -> None:
    now = datetime(2026, 7, 31, tzinfo=UTC)
    store = MemoryCheckpointStore()
    store.checkpoint = LongMediaCheckpoint(
        ATTEMPT,
        "a" * 64,
        "b" * 64,
        now,
        now.replace(day=31) + __import__("datetime").timedelta(days=7),
        (
            CheckpointChunk(0, 0, 4_000, ChunkCheckpointState.AMBIGUOUS, attempts=1),
            CheckpointChunk(1, 2_000, 6_000, ChunkCheckpointState.PENDING),
        ),
    )
    paused, provider, _, _, _, _ = _workflow([], store)

    result = paused.execute(_command())

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is AttemptFailure.AMBIGUOUS
    assert provider.calls == []

    resumed, resumed_provider, _, _, _, _ = _workflow([_success("um"), _success("dois")], store)
    assert isinstance(
        resumed.execute(_command(confirm_ambiguous=True)), TranscribeSingleFileSuccess
    )
    assert len(resumed_provider.calls) == 2


def test_provider_cancellation_removes_checkpoint_and_never_writes() -> None:
    cancelled = TranscriptionFailure(ProviderFailure.CANCELLED, False, "cancelled", "CANCELLED")
    use_case, _, _, store, writer, _ = _workflow([cancelled])

    result = use_case.execute(_command())

    assert isinstance(result, TranscribeSingleFileFailure)
    assert result.category is AttemptFailure.CANCELLED
    assert store.checkpoint is None
    assert writer.calls == []
