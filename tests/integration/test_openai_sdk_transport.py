from collections.abc import Callable

import httpx
import pytest

from caleo_transcriber.adapters.openai import OpenAISdkTransport, SdkTranscriptionRequest
from caleo_transcriber.adapters.openai.whisper import OpenAITransportError, TransportFailure
from caleo_transcriber.application import SecretValue

pytestmark = pytest.mark.integration
CANARY_KEY = "synthetic-http-key"
CANARY_AUDIO = b"synthetic-audio-content"


def _factory(handler: Callable[[httpx.Request], httpx.Response]) -> Callable[[], httpx.Client]:
    return lambda: httpx.Client(transport=httpx.MockTransport(handler))


def test_sdk_builds_expected_multipart_without_source_path_or_retry() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            request=request,
            json={
                "task": "transcribe",
                "language": "pt",
                "duration": 1.0,
                "text": "Olá",
                "segments": [{"id": 0, "start": 0.0, "end": 1.0, "text": "Olá"}],
            },
        )

    transport = OpenAISdkTransport(_factory(handler))
    response = transport.transcribe(
        SecretValue(CANARY_KEY), SdkTranscriptionRequest(audio=CANARY_AUDIO, language="pt")
    )

    assert response["text"] == "Olá"
    assert len(captured) == 1
    request = captured[0]
    body = request.content
    assert request.url.path == "/v1/audio/transcriptions"
    assert b'name="model"' in body and b"whisper-1" in body
    assert b'name="response_format"' in body and b"verbose_json" in body
    assert b'name="timestamp_granularities[]"' in body and b"segment" in body
    assert b'filename="audio.mp3"' in body
    assert CANARY_AUDIO in body
    assert b"private recording" not in body
    assert request.headers["authorization"] == f"Bearer {CANARY_KEY}"


@pytest.mark.parametrize(
    ("status", "expected"),
    [(401, 401), (403, 403), (429, 429), (500, 500)],
)
def test_sdk_disables_automatic_retries_and_reduces_http_errors(status: int, expected: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status, request=request, json={"error": {"message": "synthetic"}})

    with pytest.raises(OpenAITransportError) as caught:
        OpenAISdkTransport(_factory(handler)).transcribe(
            SecretValue(CANARY_KEY), SdkTranscriptionRequest(audio=CANARY_AUDIO)
        )

    assert calls == 1
    assert caught.value.reason is TransportFailure.STATUS
    assert caught.value.status_code == expected


def test_sdk_maps_timeout_without_leaking_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    with pytest.raises(OpenAITransportError) as caught:
        OpenAISdkTransport(_factory(handler), timeout_seconds=1).transcribe(
            SecretValue(CANARY_KEY), SdkTranscriptionRequest(audio=CANARY_AUDIO)
        )

    assert caught.value.reason is TransportFailure.TIMEOUT
    assert CANARY_KEY not in str(caught.value)
