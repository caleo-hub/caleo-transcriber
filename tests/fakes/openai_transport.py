from collections.abc import Mapping

from caleo_transcriber.adapters.openai.whisper import (
    OpenAITranscriptionTransport,
    SdkTranscriptionRequest,
)
from caleo_transcriber.application import SecretValue


class SpyOpenAITransport(OpenAITranscriptionTransport):
    def __init__(self, response: Mapping[str, object] | Exception) -> None:
        self.response = response
        self.calls: list[SdkTranscriptionRequest] = []
        self.secrets: list[SecretValue] = []

    def transcribe(
        self, api_key: SecretValue, request: SdkTranscriptionRequest
    ) -> Mapping[str, object]:
        self.calls.append(request)
        self.secrets.append(api_key)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response
