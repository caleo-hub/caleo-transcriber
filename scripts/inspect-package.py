"""Inspeciona o candidato sem imprimir nomes ou conteúdo sensível."""

import argparse
import struct
from pathlib import Path

FORBIDDEN_SUFFIXES = {".mp3", ".mp4", ".wav", ".log", ".tmp"}
CANARIES = (
    b"synthetic-openai-key",
    b"synthetic-audio-content",
    "Texto sintético".encode(),
    b"private recording",
)
REQUIRED = (
    "CaleoTranscriber.exe",
    "ffmpeg/ffmpeg.exe",
    "ffmpeg/ffprobe.exe",
    "THIRD_PARTY.md",
    "licenses/LGPL-3.0.txt",
)


def _contains_canary(path: Path, canaries: tuple[bytes, ...]) -> bool:
    overlap = max(map(len, canaries)) - 1
    previous = b""
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            combined = previous + chunk
            if any(canary in combined for canary in canaries):
                return True
            previous = combined[-overlap:]
    return False


def _pe_machine(path: Path) -> int:
    with path.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("PACKAGE_EXECUTABLE_NOT_PE")
        stream.seek(0x3C)
        pe_offset = struct.unpack("<I", stream.read(4))[0]
        stream.seek(pe_offset)
        if stream.read(4) != b"PE\0\0":
            raise ValueError("PACKAGE_EXECUTABLE_NOT_PE")
        return int(struct.unpack("<H", stream.read(2))[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--forbidden-path-fragment", action="append", default=[])
    arguments = parser.parse_args()
    root = arguments.package.resolve(strict=True)
    dynamic_canaries = tuple(
        str(fragment).encode("utf-8") for fragment in arguments.forbidden_path_fragment
    )
    canaries = CANARIES + dynamic_canaries

    missing = [relative for relative in REQUIRED if not (root / relative).is_file()]
    if missing:
        raise ValueError("PACKAGE_REQUIRED_FILE_MISSING")
    if _pe_machine(root / "CaleoTranscriber.exe") != 0x8664:
        raise ValueError("PACKAGE_EXECUTABLE_NOT_X64")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name.lower().startswith(".env"):
            raise ValueError("PACKAGE_FORBIDDEN_FILE")
        if _contains_canary(path, canaries):
            raise ValueError("PACKAGE_CANARY_FOUND")
    print("package-inspection: ok architecture=x64 forbidden_files=0 canaries=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
