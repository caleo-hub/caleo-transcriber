from pathlib import Path

EXPECTED_TAG = "autobuild-2026-07-31-14-10"
EXPECTED_SHA256 = "089e4169e93b2b3f3acbfced3c0704d24276a225641bdda04d796d28b07a2a38"


def test_ffmpeg_fetch_is_pinned_to_immutable_release_and_sha256() -> None:
    script = Path("scripts/fetch-ffmpeg.ps1").read_text(encoding="utf-8-sig")

    assert EXPECTED_TAG in script
    assert "/releases/download/$releaseTag/$archiveName" in script
    assert EXPECTED_SHA256 in script
    assert "latest" not in script.lower()


def test_ffmpeg_binary_cache_is_excluded_from_git() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8-sig")

    assert "vendor/ffmpeg/bin/" in gitignore
