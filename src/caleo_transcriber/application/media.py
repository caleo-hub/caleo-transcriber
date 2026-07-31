"""Contratos neutros para análise e preparação de mídia."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import TracebackType
from typing import Protocol, Self, runtime_checkable


class MediaFailure(StrEnum):
    MISSING = "missing"
    EMPTY = "empty"
    UNSUPPORTED = "unsupported"
    CORRUPT = "corrupt"
    NO_AUDIO = "no_audio"
    INVALID_DURATION = "invalid_duration"
    DURATION_LIMIT = "duration_limit"
    PROVIDER_LIMIT = "provider_limit"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PROCESSING = "processing"


class MediaError(RuntimeError):
    """Falha estável que não inclui caminhos ou saída bruta de processos."""

    def __init__(self, reason: MediaFailure) -> None:
        self.reason = reason
        super().__init__(f"Media operation failed: {reason.value}")


@dataclass(frozen=True, slots=True)
class MediaInfo:
    duration_seconds: float
    format_name: str
    has_audio: bool
    has_video: bool


@dataclass(frozen=True, slots=True)
class PreparedAudio:
    path: Path
    duration_seconds: float
    size_bytes: int
    media_type: str = "audio/mpeg"


@runtime_checkable
class MediaProbe(Protocol):
    def probe(self, source: Path) -> MediaInfo: ...


@runtime_checkable
class PreparedAudioLease(Protocol):
    def __enter__(self) -> Self: ...

    @property
    def audio(self) -> PreparedAudio: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


@runtime_checkable
class AudioExtractor(Protocol):
    def prepare(
        self,
        source: Path,
        info: MediaInfo,
        workspace: Path,
        should_cancel: Callable[[], bool] | None = None,
    ) -> PreparedAudioLease: ...
