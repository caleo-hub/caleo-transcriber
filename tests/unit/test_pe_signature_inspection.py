import importlib.util
import struct
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).parents[2]


def _load_inspector() -> ModuleType:
    path = PROJECT_ROOT / "scripts/inspect-pe-signature.py"
    spec = importlib.util.spec_from_file_location("inspect_pe_signature", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_pe(path: Path, certificate_offset: int, certificate_size: int) -> None:
    pe_offset = 0x80
    optional_size = 240
    image = bytearray(pe_offset + 4 + 20 + optional_size)
    image[:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, pe_offset)
    image[pe_offset : pe_offset + 4] = b"PE\0\0"
    coff_offset = pe_offset + 4
    struct.pack_into("<H", image, coff_offset + 16, optional_size)
    optional_offset = coff_offset + 20
    struct.pack_into("<H", image, optional_offset, 0x20B)
    struct.pack_into("<I", image, optional_offset + 108, 16)
    security_offset = optional_offset + 112 + 4 * 8
    struct.pack_into("<II", image, security_offset, certificate_offset, certificate_size)
    path.write_bytes(image)


def test_unsigned_pe_has_empty_authenticode_table(tmp_path: Path) -> None:
    inspector = _load_inspector()
    executable = tmp_path / "unsigned.exe"
    _write_pe(executable, 0, 0)

    assert inspector.authenticode_table(executable) == (0, 0)


def test_signed_pe_exposes_authenticode_table(tmp_path: Path) -> None:
    inspector = _load_inspector()
    executable = tmp_path / "signed.exe"
    _write_pe(executable, 4096, 512)

    assert inspector.authenticode_table(executable) == (4096, 512)


def test_malformed_input_is_rejected(tmp_path: Path) -> None:
    inspector = _load_inspector()
    executable = tmp_path / "invalid.exe"
    executable.write_bytes(b"not a PE")

    with pytest.raises(ValueError, match="PE_SIGNATURE_NOT_PE"):
        inspector.authenticode_table(executable)
