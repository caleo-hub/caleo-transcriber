import json
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]


@pytest.mark.integration
def test_runtime_sbom_is_spdx_and_contains_direct_dependencies(tmp_path: Path) -> None:
    output = tmp_path / "sbom.spdx.json"
    licenses = tmp_path / "licenses"
    subprocess.run(  # noqa: S603 - executável Python atual e argumentos controlados
        [
            str(PROJECT_ROOT / ".venv/Scripts/python.exe"),
            str(PROJECT_ROOT / "scripts/generate-sbom.py"),
            "--version",
            "0.1.0",
            "--commit",
            "synthetic-commit",
            "--created",
            "2026-07-31T00:00:00Z",
            "--output",
            str(output),
            "--licenses-dir",
            str(licenses),
        ],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        shell=False,
        timeout=30,
    )

    document = json.loads(output.read_text(encoding="utf-8"))
    names = {package["name"].lower() for package in document["packages"]}
    assert document["spdxVersion"] == "SPDX-2.3"
    assert document["dataLicense"] == "CC0-1.0"
    assert {"caleo-transcriber", "keyring", "openai", "pyside6"} <= names
    assert list(licenses.rglob("*"))
