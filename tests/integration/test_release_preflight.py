import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
PREFLIGHT = PROJECT_ROOT / "scripts" / "release-preflight.ps1"
VERSION = "0.1.0-test"
INSTALLER_NAME = f"CaleoTranscriber-Setup-{VERSION}-x64.exe"


def _write_candidate(directory: Path) -> Path:
    installer = directory / INSTALLER_NAME
    installer.write_bytes(b"synthetic-installer")
    digest = hashlib.sha256(installer.read_bytes()).hexdigest()
    (directory / "SHA256SUMS.txt").write_text(f"{digest}  {INSTALLER_NAME}\n", encoding="utf-8")
    (directory / "sbom.spdx.json").write_text('{"spdxVersion":"SPDX-2.3"}\n', encoding="utf-8")
    (directory / "THIRD_PARTY.md").write_text("synthetic dependency\n", encoding="utf-8")
    (directory / "RELEASE_NOTES.md").write_text("# Synthetic candidate\n", encoding="utf-8")
    return installer


def _run_preflight(directory: Path) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell.exe")
    assert powershell is not None
    return subprocess.run(  # noqa: S603
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PREFLIGHT),
            "-Version",
            VERSION,
            "-CandidateDirectory",
            str(directory),
        ],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )


@pytest.mark.integration
def test_release_preflight_accepts_coherent_candidate(tmp_path: Path) -> None:
    _write_candidate(tmp_path)

    result = _run_preflight(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "release-preflight: ok" in result.stdout


@pytest.mark.integration
def test_release_preflight_rejects_checksum_mismatch(tmp_path: Path) -> None:
    installer = _write_candidate(tmp_path)
    installer.write_bytes(b"tampered-installer")

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert "PREFLIGHT_CHECKSUM_MISMATCH" in result.stderr


@pytest.mark.integration
def test_release_preflight_rejects_missing_required_file(tmp_path: Path) -> None:
    _write_candidate(tmp_path)
    (tmp_path / "sbom.spdx.json").unlink()

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert "PREFLIGHT_MISSING_FILE" in result.stderr


@pytest.mark.integration
def test_release_preflight_rejects_invalid_sbom(tmp_path: Path) -> None:
    _write_candidate(tmp_path)
    (tmp_path / "sbom.spdx.json").write_text("not-json\n", encoding="utf-8")

    result = _run_preflight(tmp_path)

    assert result.returncode != 0
    assert "PREFLIGHT_INVALID_SBOM" in result.stderr
