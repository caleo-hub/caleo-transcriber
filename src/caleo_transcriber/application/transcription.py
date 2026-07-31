"""Contrato interno do provedor de transcrição."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol, runtime_checkable


class ProviderFailure(StrEnum):
    CREDENTIAL = "credential"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    PROVIDER = "provider"
    PROVIDER_LIMIT = "provider_limit"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class TranscriptionRequest:
    attempt_id: str
    audio_path: Path
    media_type: str
    size_bytes: int
    language: str | None = None


@dataclass(frozen=True, slots=True)
class TranscriptionSegment:
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True, slots=True)
class TranscriptionSuccess:
    text: str
    detected_language: str | None
    duration_ms: int
    segments: tuple[TranscriptionSegment, ...]
    provider: str = "openai"
    model: str = "whisper-1"
    warnings: tuple[str, ...] = ()
    status: str = "success"


@dataclass(frozen=True, slots=True)
class TranscriptionFailure:
    category: ProviderFailure
    retryable: bool
    user_message_key: str
    diagnostic_code: str
    status: str = "failure"


type TranscriptionResult = TranscriptionSuccess | TranscriptionFailure


@runtime_checkable
class TranscriptionProvider(Protocol):
    def transcribe(
        self,
        request: TranscriptionRequest,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscriptionResult: ...
