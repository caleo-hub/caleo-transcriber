"""Publicação atômica de TXT e SRT consolidados."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from caleo_transcriber.application.output import OutputFormat
from caleo_transcriber.domain.long_media import TimedText

from .atomic_txt import AtomicTxtOutputWriter


class AtomicTranscriptOutputWriter:
    """Renderiza uma vez e reutiliza a política exclusiva do writer atômico."""

    def write_transcript(
        self,
        output_directory: Path,
        source_name: str,
        segments: tuple[TimedText, ...],
        output_format: OutputFormat,
        should_cancel: Callable[[], bool] | None = None,
    ) -> Path:
        text = render_txt(segments) if output_format is OutputFormat.TXT else render_srt(segments)
        writer = AtomicTxtOutputWriter(extension=output_format.value)
        return writer.write(output_directory, source_name, text, should_cancel)


def render_txt(segments: Sequence[TimedText]) -> str:
    return " ".join(segment.text.strip() for segment in segments if segment.text.strip())


def render_srt(segments: Sequence[TimedText]) -> str:
    if not segments:
        return ""
    blocks: list[str] = []
    previous_end = -1
    for index, segment in enumerate(segments, start=1):
        if segment.start_ms < previous_end or segment.end_ms <= segment.start_ms:
            raise ValueError("segmentos inválidos para SRT")
        previous_end = segment.end_ms
        blocks.append(
            f"{index}\n{_srt_timestamp(segment.start_ms)} --> "
            f"{_srt_timestamp(segment.end_ms)}\n{segment.text.strip()}"
        )
    return "\n\n".join(blocks) + "\n"


def _srt_timestamp(milliseconds: int) -> str:
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
