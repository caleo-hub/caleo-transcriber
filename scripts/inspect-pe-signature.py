"""Verifica de forma determinística se um PE contém certificado Authenticode."""

import argparse
import struct
from pathlib import Path

PE32_MAGIC = 0x10B
PE32_PLUS_MAGIC = 0x20B
SECURITY_DIRECTORY_INDEX = 4


def authenticode_table(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("PE_SIGNATURE_NOT_PE")
        stream.seek(0x3C)
        raw_offset = stream.read(4)
        if len(raw_offset) != 4:
            raise ValueError("PE_SIGNATURE_TRUNCATED")
        pe_offset = struct.unpack("<I", raw_offset)[0]
        stream.seek(pe_offset)
        if stream.read(4) != b"PE\0\0":
            raise ValueError("PE_SIGNATURE_NOT_PE")

        coff_header = stream.read(20)
        if len(coff_header) != 20:
            raise ValueError("PE_SIGNATURE_TRUNCATED")
        optional_size = struct.unpack_from("<H", coff_header, 16)[0]
        optional_header = stream.read(optional_size)
        if len(optional_header) != optional_size:
            raise ValueError("PE_SIGNATURE_TRUNCATED")

    if len(optional_header) < 2:
        raise ValueError("PE_SIGNATURE_TRUNCATED")
    magic = struct.unpack_from("<H", optional_header)[0]
    if magic == PE32_MAGIC:
        directory_offset = 96
        count_offset = 92
    elif magic == PE32_PLUS_MAGIC:
        directory_offset = 112
        count_offset = 108
    else:
        raise ValueError("PE_SIGNATURE_OPTIONAL_HEADER_INVALID")

    required_size = directory_offset + (SECURITY_DIRECTORY_INDEX + 1) * 8
    if len(optional_header) < required_size:
        raise ValueError("PE_SIGNATURE_DIRECTORY_MISSING")
    directory_count = struct.unpack_from("<I", optional_header, count_offset)[0]
    if directory_count <= SECURITY_DIRECTORY_INDEX:
        raise ValueError("PE_SIGNATURE_DIRECTORY_MISSING")

    entry_offset = directory_offset + SECURITY_DIRECTORY_INDEX * 8
    return tuple(struct.unpack_from("<II", optional_header, entry_offset))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--expect-unsigned", action="store_true")
    arguments = parser.parse_args()

    certificate_offset, certificate_size = authenticode_table(arguments.executable)
    signed = certificate_offset != 0 or certificate_size != 0
    if arguments.expect_unsigned and signed:
        raise ValueError("PE_SIGNATURE_UNEXPECTED_AUTHENTICODE")
    state = "present" if signed else "absent"
    print(f"pe-signature: ok authenticode={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
