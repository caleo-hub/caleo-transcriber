"""Fakes observáveis para o caso de uso de arquivo único."""

from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from typing import Self

from caleo_transcriber.application import (
    AttemptEvent,
    MediaError,
    MediaInfo,
    PreparedAudio,
    TranscriptionRequest,
    TranscriptionResult,
)


class FakeMediaProbe:
    def __init__(self, result: MediaInfo | MediaError) -> None:
        self.result = result
        self.calls: list[Path] = []

    def probe(self, source: Path) -> MediaInfo:
        self.calls.append(source)
        if isinstance(self.result, MediaError):
            raise self.result
        return self.result


class FakePreparedAudioLease:
    def __init__(self, audio: PreparedAudio, enter_error: MediaError | None = None) -> None:
        self._prepared = audio
        self._enter_error = enter_error
        self.entered = False
        self.exited = False

    @property
    def audio(self) -> PreparedAudio:
        if not self.entered or self.exited:
            raise RuntimeError("Audio outside lease")
        return self._prepared

    def __enter__(self) -> Self:
        self.entered = True
        self.exited = False
        if self._enter_error is not None:
            self.exited = True
            raise self._enter_error
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True


class FakeAudioExtractor:
    def __init__(self, lease: FakePreparedAudioLease) -> None:
        self.lease = lease
        self.calls: list[tuple[Path, MediaInfo, Path]] = []

    def prepare(
        self,
        source: Path,
        info: MediaInfo,
        workspace: Path,
        should_cancel: Callable[[], bool] | None = None,
    ) -> FakePreparedAudioLease:
        self.calls.append((source, info, workspace))
        return self.lease


class FakeTranscriptionProvider:
    def __init__(
        self,
        results: TranscriptionResult | list[TranscriptionResult],
        before_return: Callable[[], None] | None = None,
    ) -> None:
        self._results = results if isinstance(results, list) else [results]
        self._before_return = before_return
        self.calls: list[TranscriptionRequest] = []

    def transcribe(
        self,
        request: TranscriptionRequest,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscriptionResult:
        self.calls.append(request)
        if self._before_return is not None:
            self._before_return()
        return self._results.pop(0)


class FakeTxtOutputWriter:
    def __init__(
        self,
        result: Path | Exception,
    ) -> None:
        self.result = result
        self.calls: list[tuple[Path, str, str]] = []

    def write(
        self,
        output_directory: Path,
        source_name: str,
        text: str,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path:
        self.calls.append((output_directory, source_name, text))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class RecordingAttemptEvents:
    def __init__(self) -> None:
        self.events: list[AttemptEvent] = []

    def publish(self, event: AttemptEvent) -> None:
        self.events.append(event)
