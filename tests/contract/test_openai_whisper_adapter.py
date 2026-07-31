from pathlib import Path

import pytest
from tests.fakes.credential_store import InMemoryCredentialStore
from tests.fakes.openai_transport import SpyOpenAITransport

from caleo_transcriber.adapters.openai import OpenAIWhisperAdapter
from caleo_transcriber.adapters.openai.whisper import OpenAITransportError, TransportFailure
from caleo_transcriber.application import (
    OPENAI_CREDENTIAL_ACCOUNT,
    OPENAI_CREDENTIAL_SERVICE,
    ProviderFailure,
    SecretValue,
    TranscriptionFailure,
    TranscriptionProvider,
    TranscriptionRequest,
    TranscriptionSuccess,
)

pytestmark = pytest.mark.contract
CANARY_KEY = "synthetic-openai-key"
CANARY_AUDIO = b"synthetic-mp3-bytes"


def _request(tmp_path: Path) -> TranscriptionRequest:
    audio = tmp_path / "private recording.mp3"
    audio.write_bytes(CANARY_AUDIO)
    return TranscriptionRequest("attempt-1", audio, "audio/mpeg", len(CANARY_AUDIO))


def _store(configured: bool = True) -> InMemoryCredentialStore:
    store = InMemoryCredentialStore()
    if configured:
        store.set(
            OPENAI_CREDENTIAL_SERVICE,
            OPENAI_CREDENTIAL_ACCOUNT,
            SecretValue(CANARY_KEY),
        )
    return store


def _response() -> dict[str, object]:
    return {
        "text": "Texto transcrito.",
        "language": "pt",
        "duration": 4.2,
        "segments": [{"start": 0.0, "end": 4.2, "text": "Texto transcrito."}],
    }


def test_adapter_sends_only_audio_with_fixed_contract(tmp_path: Path) -> None:
    transport = SpyOpenAITransport(_response())
    adapter = OpenAIWhisperAdapter(_store(), transport)

    assert isinstance(adapter, TranscriptionProvider)
    result = adapter.transcribe(_request(tmp_path))

    assert isinstance(result, TranscriptionSuccess)
    assert result.text == "Texto transcrito."
    assert result.duration_ms == 4200
    assert result.segments[0].end_ms == 4200
    assert len(transport.calls) == 1
    sent = transport.calls[0]
    assert sent.audio == CANARY_AUDIO
    assert sent.filename == "audio.mp3"
    assert sent.media_type == "audio/mpeg"
    assert sent.model == "whisper-1"
    assert sent.response_format == "verbose_json"
    assert sent.timestamp_granularities == ("segment",)
    assert "private recording" not in repr(sent)
    assert CANARY_KEY not in repr(transport.secrets)


def test_silence_is_success_with_warning(tmp_path: Path) -> None:
    response: dict[str, object] = {
        "text": "",
        "language": None,
        "duration": 60.0,
        "segments": [],
    }

    result = OpenAIWhisperAdapter(_store(), SpyOpenAITransport(response)).transcribe(
        _request(tmp_path)
    )

    assert isinstance(result, TranscriptionSuccess)
    assert result.warnings == ("no_speech_detected",)


@pytest.mark.parametrize(
    ("error", "category", "retryable", "code"),
    [
        (
            OpenAITransportError(TransportFailure.STATUS, 401),
            ProviderFailure.CREDENTIAL,
            False,
            "OPENAI_401",
        ),
        (
            OpenAITransportError(TransportFailure.STATUS, 403),
            ProviderFailure.CREDENTIAL,
            False,
            "OPENAI_403",
        ),
        (
            OpenAITransportError(TransportFailure.STATUS, 429),
            ProviderFailure.RATE_LIMIT,
            True,
            "OPENAI_429",
        ),
        (
            OpenAITransportError(TransportFailure.TIMEOUT),
            ProviderFailure.NETWORK,
            True,
            "OPENAI_TIMEOUT",
        ),
        (
            OpenAITransportError(TransportFailure.NETWORK),
            ProviderFailure.NETWORK,
            True,
            "OPENAI_NETWORK",
        ),
        (
            OpenAITransportError(TransportFailure.STATUS, 500),
            ProviderFailure.PROVIDER,
            True,
            "OPENAI_5XX",
        ),
    ],
)
def test_transport_errors_map_to_stable_failure(
    tmp_path: Path,
    error: Exception,
    category: ProviderFailure,
    retryable: bool,
    code: str,
) -> None:
    result = OpenAIWhisperAdapter(_store(), SpyOpenAITransport(error)).transcribe(
        _request(tmp_path)
    )

    assert isinstance(result, TranscriptionFailure)
    assert result.category is category
    assert result.retryable is retryable
    assert result.diagnostic_code == code
    assert CANARY_KEY not in repr(result)


def test_missing_credential_and_cancel_do_not_call_transport(tmp_path: Path) -> None:
    transport = SpyOpenAITransport(_response())
    request = _request(tmp_path)

    missing = OpenAIWhisperAdapter(_store(False), transport).transcribe(request)
    cancelled = OpenAIWhisperAdapter(_store(), transport).transcribe(request, lambda: True)

    assert isinstance(missing, TranscriptionFailure)
    assert missing.category is ProviderFailure.CREDENTIAL
    assert isinstance(cancelled, TranscriptionFailure)
    assert cancelled.category is ProviderFailure.CANCELLED
    assert transport.calls == []


def test_invalid_response_becomes_provider_failure(tmp_path: Path) -> None:
    invalid = {"text": "partial", "language": "pt", "duration": 1.0, "segments": "bad"}

    result = OpenAIWhisperAdapter(_store(), SpyOpenAITransport(invalid)).transcribe(
        _request(tmp_path)
    )

    assert isinstance(result, TranscriptionFailure)
    assert result.diagnostic_code == "OPENAI_RESPONSE_INVALID"
