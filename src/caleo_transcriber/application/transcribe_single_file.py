"""Orquestra a primeira fatia sem conhecer adapters ou frameworks."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from threading import Lock
from typing import Protocol, runtime_checkable

from caleo_transcriber.application.media import (
    AudioExtractor,
    MediaError,
    MediaFailure,
    MediaProbe,
)
from caleo_transcriber.application.output import (
    OutputWriteCancelled,
    OutputWriteError,
    TxtOutputWriter,
)
from caleo_transcriber.application.transcription import (
    ProviderFailure,
    TranscriptionFailure,
    TranscriptionProvider,
    TranscriptionRequest,
)
from caleo_transcriber.domain import AttemptState, require_transition


class AttemptFailure(StrEnum):
    INVALID_INPUT = "invalid_input"
    UNSUPPORTED_MEDIA = "unsupported_media"
    CREDENTIAL = "credential"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    PROVIDER = "provider"
    CANCELLED = "cancelled"
    OUTPUT = "output"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class TranscribeSingleFileCommand:
    attempt_id: str
    source: Path
    output_directory: Path
    workspace: Path
    language: str | None = None


@dataclass(frozen=True, slots=True)
class AttemptEvent:
    attempt_id: str
    state: AttemptState
    failure: AttemptFailure | None = None
    warnings: tuple[str, ...] = ()
    completed_chunks: int = 0
    total_chunks: int | None = None
    active_chunk: int | None = None


@runtime_checkable
class AttemptEvents(Protocol):
    def publish(self, event: AttemptEvent) -> None: ...


@dataclass(frozen=True, slots=True)
class TranscribeSingleFileSuccess:
    attempt_id: str
    output_path: Path
    warnings: tuple[str, ...]
    state: AttemptState = AttemptState.COMPLETED


@dataclass(frozen=True, slots=True)
class TranscribeSingleFileFailure:
    attempt_id: str
    category: AttemptFailure
    retryable: bool
    user_message_key: str
    diagnostic_code: str
    state: AttemptState


type TranscribeSingleFileResult = TranscribeSingleFileSuccess | TranscribeSingleFileFailure


@runtime_checkable
class TranscribeSingleFileUseCase(Protocol):
    def execute(
        self,
        command: TranscribeSingleFileCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult: ...


class TranscriptionAlreadyRunningError(RuntimeError):
    """Impede duas tentativas simultâneas no incremento de arquivo único."""

    def __init__(self) -> None:
        super().__init__("A transcription attempt is already running")


class TranscribeSingleFile:
    def __init__(
        self,
        media_probe: MediaProbe,
        audio_extractor: AudioExtractor,
        provider: TranscriptionProvider,
        output_writer: TxtOutputWriter,
        events: AttemptEvents,
    ) -> None:
        self._media_probe = media_probe
        self._audio_extractor = audio_extractor
        self._provider = provider
        self._output_writer = output_writer
        self._events = events
        self._active = Lock()

    def execute(
        self,
        command: TranscribeSingleFileCommand,
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
        command: TranscribeSingleFileCommand,
        should_cancel: Callable[[], bool],
    ) -> TranscribeSingleFileResult:
        state = AttemptState.READY
        self._publish(command.attempt_id, state)
        state = self._transition(command.attempt_id, state, AttemptState.PREPARING)
        if should_cancel():
            return self._cancel(command.attempt_id, state)

        try:
            info = self._media_probe.probe(command.source)
            with self._audio_extractor.prepare(
                command.source, info, command.workspace, should_cancel
            ) as lease:
                if should_cancel():
                    return self._cancel(command.attempt_id, state)
                state = self._transition(command.attempt_id, state, AttemptState.TRANSCRIBING)
                audio = lease.audio
                transcription = self._provider.transcribe(
                    TranscriptionRequest(
                        attempt_id=command.attempt_id,
                        audio_path=audio.path,
                        media_type=audio.media_type,
                        size_bytes=audio.size_bytes,
                        language=command.language,
                    ),
                    should_cancel,
                )
                if isinstance(transcription, TranscriptionFailure):
                    if transcription.category is ProviderFailure.CANCELLED:
                        return self._cancel(command.attempt_id, state)
                    return self._fail(
                        command.attempt_id,
                        state,
                        _provider_category(transcription.category),
                        transcription.retryable,
                        transcription.user_message_key,
                        transcription.diagnostic_code,
                    )
                if should_cancel():
                    return self._cancel(command.attempt_id, state)
                state = self._transition(command.attempt_id, state, AttemptState.SAVING)
                try:
                    output = self._output_writer.write(
                        command.output_directory,
                        command.source.name,
                        transcription.text,
                        should_cancel,
                    )
                except OutputWriteCancelled:
                    return self._cancel(command.attempt_id, state)
                except OutputWriteError:
                    return self._fail(
                        command.attempt_id,
                        state,
                        AttemptFailure.OUTPUT,
                        True,
                        "transcription.error.output",
                        "OUTPUT_WRITE",
                    )
                warnings = transcription.warnings
            state = self._transition(
                command.attempt_id,
                state,
                AttemptState.COMPLETED,
                warnings=warnings,
            )
            return TranscribeSingleFileSuccess(command.attempt_id, output, warnings, state)
        except MediaError as error:
            if error.reason is MediaFailure.CANCELLED:
                return self._cancel(command.attempt_id, state)
            category = _media_category(error.reason)
            return self._fail(
                command.attempt_id,
                state,
                category,
                error.reason in {MediaFailure.TIMEOUT, MediaFailure.PROCESSING},
                f"transcription.error.{category.value}",
                f"MEDIA_{error.reason.value.upper()}",
            )

    def _transition(
        self,
        attempt_id: str,
        current: AttemptState,
        target: AttemptState,
        *,
        failure: AttemptFailure | None = None,
        warnings: tuple[str, ...] = (),
    ) -> AttemptState:
        state = require_transition(current, target)
        self._publish(attempt_id, state, failure, warnings)
        return state

    def _cancel(self, attempt_id: str, current: AttemptState) -> TranscribeSingleFileFailure:
        state = self._transition(attempt_id, current, AttemptState.CANCELLING)
        state = self._transition(
            attempt_id, state, AttemptState.CANCELLED, failure=AttemptFailure.CANCELLED
        )
        return TranscribeSingleFileFailure(
            attempt_id,
            AttemptFailure.CANCELLED,
            False,
            "transcription.error.cancelled",
            "ATTEMPT_CANCELLED",
            state,
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
        state = self._transition(attempt_id, current, AttemptState.FAILED, failure=category)
        return TranscribeSingleFileFailure(
            attempt_id,
            category,
            retryable,
            user_message_key,
            diagnostic_code,
            state,
        )

    def _publish(
        self,
        attempt_id: str,
        state: AttemptState,
        failure: AttemptFailure | None = None,
        warnings: tuple[str, ...] = (),
    ) -> None:
        self._events.publish(AttemptEvent(attempt_id, state, failure, warnings))


def _media_category(reason: MediaFailure) -> AttemptFailure:
    if reason is MediaFailure.UNSUPPORTED:
        return AttemptFailure.UNSUPPORTED_MEDIA
    if reason in {
        MediaFailure.MISSING,
        MediaFailure.EMPTY,
        MediaFailure.CORRUPT,
        MediaFailure.NO_AUDIO,
        MediaFailure.INVALID_DURATION,
        MediaFailure.DURATION_LIMIT,
    }:
        return AttemptFailure.INVALID_INPUT
    return AttemptFailure.PROVIDER


def _provider_category(reason: ProviderFailure) -> AttemptFailure:
    mapping = {
        ProviderFailure.CREDENTIAL: AttemptFailure.CREDENTIAL,
        ProviderFailure.NETWORK: AttemptFailure.NETWORK,
        ProviderFailure.RATE_LIMIT: AttemptFailure.RATE_LIMIT,
        ProviderFailure.PROVIDER: AttemptFailure.PROVIDER,
        ProviderFailure.PROVIDER_LIMIT: AttemptFailure.PROVIDER,
        ProviderFailure.CANCELLED: AttemptFailure.CANCELLED,
    }
    return mapping[reason]
