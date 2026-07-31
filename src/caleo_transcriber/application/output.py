"""Porta para criação segura de arquivos finais de transcrição."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol, runtime_checkable


class OutputWriteError(RuntimeError):
    """Falha neutra ao criar a saída final."""

    def __init__(self) -> None:
        super().__init__("Não foi possível criar o arquivo de saída.")


class OutputWriteCancelled(RuntimeError):
    """Escrita interrompida antes da publicação do arquivo final."""


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
