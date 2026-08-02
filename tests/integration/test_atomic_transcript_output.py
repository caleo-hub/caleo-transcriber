import re
from pathlib import Path

import pytest

from caleo_transcriber.adapters.filesystem import (
    AtomicTranscriptOutputWriter,
    render_srt,
    render_txt,
)
from caleo_transcriber.application import OutputFormat, TranscriptOutputWriter
from caleo_transcriber.domain import TimedText

pytestmark = pytest.mark.integration

_CUE = re.compile(
    r"(?m)^(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> "
    r"(\d{2}:\d{2}:\d{2},\d{3})\n(.+)$"
)


def _segments() -> tuple[TimedText, ...]:
    return (
        TimedText(3_723_004, 3_724_500, "Olá, 日本語 🎙️"),
        TimedText(3_724_500, 3_726_000, "Segundo trecho."),
    )


def test_txt_and_srt_derive_from_same_segments_without_retranscription(tmp_path: Path) -> None:
    writer = AtomicTranscriptOutputWriter()
    segments = _segments()

    assert isinstance(writer, TranscriptOutputWriter)
    txt = writer.write_transcript(tmp_path, "reunião.mp4", segments, OutputFormat.TXT)
    srt = writer.write_transcript(tmp_path, "reunião.mp4", segments, OutputFormat.SRT)

    assert txt.read_text(encoding="utf-8") == "Olá, 日本語 🎙️ Segundo trecho."
    assert srt.read_text(encoding="utf-8") == render_srt(segments)
    assert txt.suffix == ".txt"
    assert srt.suffix == ".srt"


def test_source_folder_name_produces_transcription_suffix(tmp_path: Path) -> None:
    writer = AtomicTranscriptOutputWriter()

    created = writer.write_transcript(tmp_path, "Demo_transcription.mp4", (), OutputFormat.TXT)

    assert created.name == "Demo_transcription.txt"


def test_srt_has_valid_global_increasing_non_overlapping_cues() -> None:
    cues = _CUE.findall(render_srt(_segments()))

    assert cues == [
        ("1", "01:02:03,004", "01:02:04,500", "Olá, 日本語 🎙️"),
        ("2", "01:02:04,500", "01:02:06,000", "Segundo trecho."),
    ]


def test_empty_silence_outputs_are_valid_and_collisions_do_not_overwrite(tmp_path: Path) -> None:
    writer = AtomicTranscriptOutputWriter()
    first = writer.write_transcript(tmp_path, "silêncio.wav", (), OutputFormat.SRT)
    second = writer.write_transcript(tmp_path, "silêncio.wav", (), OutputFormat.SRT)

    assert render_txt(()) == ""
    assert first.read_bytes() == b""
    assert first.name == "silêncio.srt"
    assert second.name == "silêncio (1).srt"


def test_srt_refuses_overlapping_sequence() -> None:
    segments = (TimedText(0, 2_000, "um"), TimedText(1_500, 3_000, "dois"))

    with pytest.raises(ValueError, match="segmentos inválidos"):
        render_srt(segments)
