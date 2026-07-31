"""Implementação do contrato v1 com whisper-1 e SDK substituível."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, cast, runtime_checkable

import httpx
import openai
from openai import OpenAI

from caleo_transcriber.application import (
    OPENAI_CREDENTIAL_ACCOUNT,
    OPENAI_CREDENTIAL_SERVICE,
    CredentialStore,
    ProviderFailure,
    SecretValue,
    TranscriptionFailure,
    TranscriptionRequest,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionSuccess,
)

MAX_AUDIO_BYTES = 25_000_000


@dataclass(frozen=True, slots=True, repr=False)
class SdkTranscriptionRequest:
    audio: bytes
    filename: str = "audio.mp3"
    media_type: str = "audio/mpeg"
    model: str = "whisper-1"
    response_format: str = "verbose_json"
    timestamp_granularities: tuple[str, ...] = ("segment",)
    language: str | None = None

    def __repr__(self) -> str:
        return "SdkTranscriptionRequest(<redacted audio>)"


class TransportFailure(StrEnum):
    NETWORK = "network"
    TIMEOUT = "timeout"
    STATUS = "status"
    RESPONSE = "response"


class OpenAITransportError(RuntimeError):
    def __init__(self, reason: TransportFailure, status_code: int | None = None) -> None:
        self.reason = reason
        self.status_code = status_code
        super().__init__("OpenAI transport failed")


@runtime_checkable
class OpenAITranscriptionTransport(Protocol):
    def transcribe(
        self, api_key: SecretValue, request: SdkTranscriptionRequest
    ) -> Mapping[str, object]: ...


class OpenAISdkTransport:
    """Fronteira fina do SDK oficial, com retry automático desativado."""

    def __init__(
        self,
        http_client_factory: Callable[[], httpx.Client] | None = None,
        timeout_seconds: float = 600.0,
    ) -> None:
        self._http_client_factory = http_client_factory or httpx.Client
        self._timeout = httpx.Timeout(
            timeout_seconds,
            connect=10.0,
            read=timeout_seconds,
            write=60.0,
            pool=10.0,
        )

    def transcribe(
        self, api_key: SecretValue, request: SdkTranscriptionRequest
    ) -> Mapping[str, object]:
        try:
            with OpenAI(
                api_key=api_key.reveal(),
                max_retries=0,
                timeout=self._timeout,
                http_client=self._http_client_factory(),
            ) as client:
                response = client.audio.transcriptions.create(
                    file=(request.filename, request.audio, request.media_type),
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language=request.language if request.language is not None else openai.omit,
                )
        except openai.APITimeoutError as error:
            raise OpenAITransportError(TransportFailure.TIMEOUT) from error
        except openai.APIConnectionError as error:
            raise OpenAITransportError(TransportFailure.NETWORK) from error
        except openai.APIStatusError as error:
            raise OpenAITransportError(TransportFailure.STATUS, error.status_code) from error
        if not hasattr(response, "model_dump"):
            raise OpenAITransportError(TransportFailure.RESPONSE)
        return cast(Mapping[str, object], response.model_dump())


class OpenAIWhisperAdapter:
    def __init__(
        self, credential_store: CredentialStore, transport: OpenAITranscriptionTransport
    ) -> None:
        self._credential_store = credential_store
        self._transport = transport

    def transcribe(
        self,
        request: TranscriptionRequest,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscriptionResult:
        cancel = should_cancel or (lambda: False)
        if cancel():
            return _failure(ProviderFailure.CANCELLED, False, "OPENAI_CANCELLED")
        precondition = self._validate_request(request)
        if precondition is not None:
            return precondition
        secret = self._credential_store.get(OPENAI_CREDENTIAL_SERVICE, OPENAI_CREDENTIAL_ACCOUNT)
        if secret is None:
            return _failure(ProviderFailure.CREDENTIAL, False, "OPENAI_CREDENTIAL_MISSING")

        try:
            audio = request.audio_path.read_bytes()
            raw = self._transport.transcribe(
                secret,
                SdkTranscriptionRequest(audio=audio, language=request.language),
            )
        except OSError:
            return _failure(ProviderFailure.PROVIDER, False, "OPENAI_AUDIO_READ")
        except OpenAITransportError as error:
            return _map_transport_error(error)
        if cancel():
            return _failure(ProviderFailure.CANCELLED, False, "OPENAI_CANCELLED")
        try:
            return _parse_success(raw)
        except (KeyError, TypeError, ValueError):
            return _failure(ProviderFailure.PROVIDER, False, "OPENAI_RESPONSE_INVALID")

    @staticmethod
    def _validate_request(request: TranscriptionRequest) -> TranscriptionFailure | None:
        if request.media_type != "audio/mpeg" or request.audio_path.suffix.lower() != ".mp3":
            return _failure(ProviderFailure.PROVIDER, False, "OPENAI_AUDIO_INVALID")
        if request.size_bytes <= 0 or request.size_bytes >= MAX_AUDIO_BYTES:
            return _failure(ProviderFailure.PROVIDER_LIMIT, False, "OPENAI_SIZE_LIMIT")
        try:
            actual_size = request.audio_path.stat().st_size
        except OSError:
            return _failure(ProviderFailure.PROVIDER, False, "OPENAI_AUDIO_READ")
        if actual_size != request.size_bytes:
            return _failure(ProviderFailure.PROVIDER, False, "OPENAI_AUDIO_CHANGED")
        return None


def _map_transport_error(error: OpenAITransportError) -> TranscriptionFailure:
    if error.reason is TransportFailure.TIMEOUT:
        return _failure(ProviderFailure.NETWORK, True, "OPENAI_TIMEOUT")
    if error.reason is TransportFailure.NETWORK:
        return _failure(ProviderFailure.NETWORK, True, "OPENAI_NETWORK")
    status = error.status_code
    if status in {401, 403}:
        return _failure(ProviderFailure.CREDENTIAL, False, f"OPENAI_{status}")
    if status == 429:
        return _failure(ProviderFailure.RATE_LIMIT, True, "OPENAI_429")
    if status is not None and status >= 500:
        return _failure(ProviderFailure.PROVIDER, True, "OPENAI_5XX")
    return _failure(ProviderFailure.PROVIDER, False, "OPENAI_PROVIDER")


def _parse_success(raw: Mapping[str, object]) -> TranscriptionSuccess:
    text = raw["text"]
    if not isinstance(text, str):
        raise TypeError
    language_value = raw.get("language")
    if language_value is not None and not isinstance(language_value, str):
        raise TypeError
    duration_ms = _milliseconds(raw["duration"])
    raw_segments = raw["segments"]
    if not isinstance(raw_segments, list):
        raise TypeError
    segments: list[TranscriptionSegment] = []
    previous_start = 0
    for raw_segment in raw_segments:
        if not isinstance(raw_segment, Mapping):
            raise TypeError
        start_ms = _milliseconds(raw_segment["start"])
        end_ms = _milliseconds(raw_segment["end"])
        segment_text = raw_segment["text"]
        if not isinstance(segment_text, str):
            raise TypeError
        if start_ms < previous_start or end_ms < start_ms or end_ms > duration_ms:
            raise ValueError
        segments.append(TranscriptionSegment(start_ms, end_ms, segment_text))
        previous_start = start_ms
    if not text and segments:
        raise ValueError
    warnings = ("no_speech_detected",) if not text else ()
    return TranscriptionSuccess(
        text=text,
        detected_language=language_value,
        duration_ms=duration_ms,
        segments=tuple(segments),
        warnings=warnings,
    )


def _milliseconds(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError
    milliseconds = round(float(value) * 1000)
    if milliseconds < 0:
        raise ValueError
    return milliseconds


def _failure(
    category: ProviderFailure, retryable: bool, diagnostic_code: str
) -> TranscriptionFailure:
    return TranscriptionFailure(
        category=category,
        retryable=retryable,
        user_message_key=f"transcription.error.{category.value}",
        diagnostic_code=diagnostic_code,
    )
