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
from caleo_transcriber.application.transcribe_single_file import (
    AttemptEvent,
    AttemptEvents,
    AttemptFailure,
    TranscribeSingleFile,
    TranscribeSingleFileCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
    TranscribeSingleFileSuccess,
    TranscribeSingleFileUseCase,
    TranscriptionAlreadyRunningError,
)
from caleo_transcriber.application.transcription import (
    ProviderFailure,
    TranscriptionFailure,
    TranscriptionProvider,
    TranscriptionRequest,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionSuccess,
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
    "ProviderFailure",
    "TranscriptionFailure",
    "TranscriptionProvider",
    "TranscriptionRequest",
    "TranscriptionResult",
    "TranscriptionSegment",
    "TranscriptionSuccess",
    "AttemptEvent",
    "AttemptEvents",
    "AttemptFailure",
    "TranscribeSingleFile",
    "TranscribeSingleFileCommand",
    "TranscribeSingleFileFailure",
    "TranscribeSingleFileResult",
    "TranscribeSingleFileSuccess",
    "TranscribeSingleFileUseCase",
    "TranscriptionAlreadyRunningError",
]
