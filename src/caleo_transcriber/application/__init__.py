"""Casos de uso e portas; sem detalhes de framework."""

from caleo_transcriber.application.api_key_settings import (
    OPENAI_CREDENTIAL_ACCOUNT,
    OPENAI_CREDENTIAL_SERVICE,
    ApiKeySettings,
    LocalKeyValidation,
)
from caleo_transcriber.application.credentials import (
    CredentialStore,
    CredentialStoreError,
    CredentialStoreFailure,
    SecretValue,
)
from caleo_transcriber.application.media import (
    AudioExtractor,
    MediaError,
    MediaFailure,
    MediaInfo,
    MediaProbe,
    PreparedAudio,
    PreparedAudioLease,
)
from caleo_transcriber.application.output import (
    OutputWriteCancelled,
    OutputWriteError,
    TxtOutputWriter,
)

__all__ = [
    "CredentialStore",
    "CredentialStoreError",
    "CredentialStoreFailure",
    "SecretValue",
    "ApiKeySettings",
    "LocalKeyValidation",
    "OPENAI_CREDENTIAL_ACCOUNT",
    "OPENAI_CREDENTIAL_SERVICE",
    "OutputWriteCancelled",
    "OutputWriteError",
    "TxtOutputWriter",
    "AudioExtractor",
    "MediaError",
    "MediaFailure",
    "MediaInfo",
    "MediaProbe",
    "PreparedAudio",
    "PreparedAudioLease",
]
