import re
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"


def source_texts() -> list[tuple[Path, str]]:
    return [(path, path.read_text(encoding="utf-8")) for path in SOURCE_ROOT.rglob("*.py")]


@pytest.mark.architecture
def test_source_never_uses_shell_true() -> None:
    violations = [
        str(path) for path, text in source_texts() if re.search(r"shell\s*=\s*True", text)
    ]
    assert violations == []


@pytest.mark.architecture
def test_source_does_not_read_openai_key_from_environment() -> None:
    violations = [str(path) for path, text in source_texts() if "OPENAI_API_KEY" in text]
    assert violations == []


@pytest.mark.architecture
def test_no_media_or_environment_file_is_tracked() -> None:
    git = shutil.which("git")
    assert git is not None
    result = subprocess.run(  # noqa: S603 - executable resolved from trusted PATH
        [git, "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    tracked = {Path(line) for line in result.stdout.splitlines()}
    forbidden_suffixes = {".mp3", ".mp4", ".wav"}
    violations = sorted(
        str(path)
        for path in tracked
        if path.suffix.lower() in forbidden_suffixes
        or (path.name.startswith(".env") and path.name != ".env.example")
    )
    assert violations == []


@pytest.mark.architecture
def test_env_example_contains_no_secret_slot() -> None:
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=" not in env_example


@pytest.mark.architecture
def test_secret_scan_requires_boundary_before_openai_key_prefix() -> None:
    audit = (PROJECT_ROOT / "scripts" / "audit.ps1").read_text(encoding="utf-8")

    assert "(^|[^A-Za-z0-9])sk-" in audit
    assert '"sk-[A-Za-z0-9_-]{20,}|' not in audit
