import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from caleo_transcriber.adapters.filesystem import AtomicTxtOutputWriter, sanitize_output_stem
from caleo_transcriber.application import OutputWriteCancelled, OutputWriteError, TxtOutputWriter

pytestmark = pytest.mark.integration


def test_writer_satisfies_port_and_writes_utf8_only_after_success(tmp_path: Path) -> None:
    writer = AtomicTxtOutputWriter()

    assert isinstance(writer, TxtOutputWriter)
    created = writer.write(tmp_path, "reunião.mp4", "Olá, mundo! 🎙️")

    assert created == tmp_path / "reunião.txt"
    assert created.read_bytes() == "Olá, mundo! 🎙️".encode()
    assert list(tmp_path.glob(".caleo-*.tmp")) == []


def test_existing_files_are_preserved_and_suffix_increments(tmp_path: Path) -> None:
    original = tmp_path / "aula.txt"
    first_collision = tmp_path / "aula (1).txt"
    original.write_bytes(b"original")
    first_collision.write_bytes(b"first")

    created = AtomicTxtOutputWriter().write(tmp_path, "aula.mp4", "new")

    assert created.name == "aula (2).txt"
    assert original.read_bytes() == b"original"
    assert first_collision.read_bytes() == b"first"
    assert created.read_text(encoding="utf-8") == "new"


def test_concurrent_writers_never_overwrite_each_other(tmp_path: Path) -> None:
    writer = AtomicTxtOutputWriter()

    with ThreadPoolExecutor(max_workers=4) as executor:
        paths = list(executor.map(lambda value: writer.write(tmp_path, "lote.wav", value), "ABCD"))

    assert len(set(paths)) == 4
    assert {path.read_text(encoding="utf-8") for path in paths} == set("ABCD")
    assert {path.name for path in paths} == {
        "lote.txt",
        "lote (1).txt",
        "lote (2).txt",
        "lote (3).txt",
    }


def test_cancel_before_publish_removes_temporary_and_final(tmp_path: Path) -> None:
    calls = 0

    def cancel_after_write() -> bool:
        nonlocal calls
        calls += 1
        return calls == 2

    with pytest.raises(OutputWriteCancelled):
        AtomicTxtOutputWriter().write(tmp_path, "cancelado.wav", "partial", cancel_after_write)

    assert list(tmp_path.iterdir()) == []


def test_publish_failure_is_neutral_and_removes_temporary(tmp_path: Path) -> None:
    with patch.object(os, "link", side_effect=OSError("sensitive path detail")):
        with pytest.raises(OutputWriteError) as caught:
            AtomicTxtOutputWriter().write(tmp_path, "falha.wav", "partial")

    assert "sensitive" not in str(caught.value)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("..\\aula?.mp4", "aula_.txt"),
        ("CON.wav", "_CON.txt"),
        ("...", "transcricao.txt"),
        ("áudio 日本語.mp3", "áudio 日本語.txt"),
    ],
)
def test_windows_output_names_are_safe(source: str, expected: str) -> None:
    assert f"{sanitize_output_stem(source)}.txt" == expected
