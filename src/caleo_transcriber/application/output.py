"""Porta para criação segura de arquivos finais de transcrição."""

from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Protocol, runtime_checkable

from caleo_transcriber.domain.long_media import TimedText


class OutputWriteError(RuntimeError):
    """Falha neutra ao criar a saída final."""

    def __init__(self) -> None:
        super().__init__("Não foi possível criar o arquivo de saída.")


class OutputWriteCancelled(RuntimeError):
    """Escrita interrompida antes da publicação do arquivo final."""


class OutputFormat(StrEnum):
    TXT = "txt"
    SRT = "srt"


@runtime_checkable
class TxtOutputWriter(Protocol):
    """Publica texto UTF-8 sem substituir arquivos existentes."""

    def write(
        self,
        output_directory: Path,
        source_name: str,
        text: str,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path:
        """Retorna o caminho exclusivo criado somente após sucesso."""
        ...


@runtime_checkable
class TranscriptOutputWriter(Protocol):
    """Publica TXT ou SRT a partir da mesma sequência consolidada."""

    def write_transcript(
        self,
        output_directory: Path,
        source_name: str,
        segments: tuple[TimedText, ...],
        output_format: OutputFormat,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path: ...
