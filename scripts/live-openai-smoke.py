"""Smoke manual pago: usa credencial do Windows e nunca imprime conteúdo."""

from __future__ import annotations

import argparse
from pathlib import Path

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.adapters.openai import OpenAISdkTransport, OpenAIWhisperAdapter
from caleo_transcriber.application import (
    TranscriptionFailure,
    TranscriptionRequest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    arguments = parser.parse_args()
    audio = arguments.audio.resolve(strict=True)
    size = audio.stat().st_size
    adapter = OpenAIWhisperAdapter(WindowsCredentialStore(), OpenAISdkTransport())
    result = adapter.transcribe(
        TranscriptionRequest("live-smoke", audio, "audio/mpeg", size)
    )
    if isinstance(result, TranscriptionFailure):
        print(
            "live-openai-smoke: failure "
            f"category={result.category.value} code={result.diagnostic_code}"
        )
        return 1
    print(
        "live-openai-smoke: ok calls=1 "
        f"duration_ms={result.duration_ms} segments={len(result.segments)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
