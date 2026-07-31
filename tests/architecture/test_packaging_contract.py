import re
from pathlib import Path

from caleo_transcriber import __version__

PROJECT_ROOT = Path(__file__).parents[2]


def test_candidate_version_is_aligned_across_runtime_and_build_metadata() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_resource = (PROJECT_ROOT / "packaging/windows-version.txt").read_text(encoding="utf-8")

    assert f'version = "{__version__}"' in pyproject
    assert f"StringStruct('ProductVersion', '{__version__}')" in version_resource
    assert f"prodvers=({', '.join(__version__.split('.'))}, 0)" in version_resource


def test_package_workflow_is_temporary_and_cannot_publish_release() -> None:
    workflow = (PROJECT_ROOT / ".github/workflows/package.yml").read_text(encoding="utf-8")

    assert "actions/upload-artifact@v7" in workflow
    assert "retention-days: 3" in workflow
    assert "contents: read" in workflow
    assert "gh release" not in workflow
    assert "OPENAI_API_KEY" not in workflow
    assert "release:" not in workflow
    assert f"run: .\\scripts\\build-package.ps1 -Version {__version__}" in workflow
    assert "run: .\\build-package.cmd" not in workflow


def test_installer_is_x64_only_non_admin_and_preserves_user_data() -> None:
    installer = (PROJECT_ROOT / "packaging/CaleoTranscriber.iss").read_text(encoding="utf-8")

    assert "ArchitecturesAllowed=x64compatible" in installer
    assert "ArchitecturesInstallIn64BitMode=x64compatible" in installer
    assert "PrivilegesRequired=lowest" in installer
    assert "MinVersion=10.0.19045" in installer
    assert "[UninstallDelete]" not in installer
    assert "[Registry]" not in installer


def test_build_scripts_pin_tools_and_never_embed_a_secret_slot() -> None:
    paths = [
        PROJECT_ROOT / "scripts/install-inno-setup.ps1",
        PROJECT_ROOT / "scripts/build-package.ps1",
        PROJECT_ROOT / "scripts/inspect-pe-signature.py",
        PROJECT_ROOT / "packaging/CaleoTranscriber.spec",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "6.7.3" in text
    assert "9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732" in text
    assert "--onedir" not in text
    assert "OPENAI_API_KEY" not in text
    assert "[switch]$RealOpenAISmoke" in text
    assert "run-once-with-synthetic-audio-owner-approved" in text
    assert not re.search(r"shell\s*=\s*True", text)
    assert "Get-AuthenticodeSignature -LiteralPath $installerPath" not in text
