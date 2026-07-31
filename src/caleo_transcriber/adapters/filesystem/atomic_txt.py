"""Publicação atômica e exclusiva de transcrições TXT."""

import os
import re
import uuid
from collections.abc import Callable
from pathlib import Path

from caleo_transcriber.application.output import OutputWriteCancelled, OutputWriteError

_INVALID_WINDOWS_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def sanitize_output_stem(source_name: str) -> str:
    """Deriva um nome Windows seguro preservando caracteres Unicode úteis."""
    name = Path(source_name).name
    stem = Path(name).stem if Path(name).suffix else name
    sanitized = _INVALID_WINDOWS_CHARACTERS.sub("_", stem).strip(" .")
    if not sanitized:
        sanitized = "transcricao"
    if sanitized.upper() in _RESERVED_WINDOWS_NAMES:
        sanitized = f"_{sanitized}"
    return sanitized[:120].rstrip(" .") or "transcricao"


class AtomicTxtOutputWriter:
    """Grava em temporário e publica por hard link exclusivo no mesmo volume."""

    def __init__(self, extension: str = "txt") -> None:
        if extension not in {"txt", "srt"}:
            raise ValueError("extensão de transcrição inválida")
        self._extension = extension

    def write(
        self,
        output_directory: Path,
        source_name: str,
        text: str,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path:
        directory = output_directory.resolve()
        stem = sanitize_output_stem(source_name)
        temporary = directory / f".caleo-{uuid.uuid4().hex}.tmp"
        cancel = should_cancel or (lambda: False)

        try:
            if cancel():
                raise OutputWriteCancelled
            with temporary.open("x", encoding="utf-8", newline="") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            if cancel():
                raise OutputWriteCancelled
            return self._publish_exclusively(temporary, directory, stem, self._extension)
        except OutputWriteCancelled:
            raise
        except OSError as error:
            raise OutputWriteError from error
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _publish_exclusively(temporary: Path, directory: Path, stem: str, extension: str) -> Path:
        suffix = 0
        while True:
            candidate_name = (
                f"{stem}.{extension}" if suffix == 0 else f"{stem} ({suffix}).{extension}"
            )
            candidate = directory / candidate_name
            try:
                os.link(temporary, candidate)
            except FileExistsError:
                suffix += 1
                continue
            return candidate
