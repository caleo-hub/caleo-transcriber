"""Adapter de transcrição OpenAI."""

from .whisper import (
    OpenAISdkTransport,
    OpenAITranscriptionTransport,
    OpenAIWhisperAdapter,
    SdkTranscriptionRequest,
)

__all__ = [
    "OpenAISdkTransport",
    "OpenAITranscriptionTransport",
    "OpenAIWhisperAdapter",
    "SdkTranscriptionRequest",
]
