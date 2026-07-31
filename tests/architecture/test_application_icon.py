import struct
from pathlib import Path

ROOT = Path(__file__).parents[2]
PNG = ROOT / "assets" / "caleo-transcriber.png"
ICO = ROOT / "assets" / "caleo-transcriber.ico"


def test_transparent_png_and_multiresolution_ico_are_valid() -> None:
    png = PNG.read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert png[25] == 6  # PNG RGBA

    ico = ICO.read_bytes()
    reserved, image_type, count = struct.unpack_from("<HHH", ico)
    assert (reserved, image_type, count) == (0, 1, 7)
    sizes = {
        (
            256 if ico[6 + index * 16] == 0 else ico[6 + index * 16],
            256 if ico[7 + index * 16] == 0 else ico[7 + index * 16],
        )
        for index in range(count)
    }
    assert sizes == {(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}


def test_packagers_and_runtime_reference_the_application_icon() -> None:
    spec = (ROOT / "packaging" / "CaleoTranscriber.spec").read_text(encoding="utf-8")
    installer = (ROOT / "packaging" / "CaleoTranscriber.iss").read_text(encoding="utf-8")
    window = (ROOT / "src" / "caleo_transcriber" / "presentation" / "main_window.py").read_text(
        encoding="utf-8"
    )

    assert "caleo-transcriber.ico" in spec
    assert "caleo-transcriber.png" in spec
    assert "SetupIconFile" in installer and "caleo-transcriber.ico" in installer
    assert "setWindowIcon" in window and "caleo-transcriber.png" in window
