# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

project_root = Path(SPEC).resolve().parents[1]
metadata = []
for distribution in ("keyring", "openai", "PySide6"):
    metadata += copy_metadata(distribution)

hidden_imports = ["keyring.backends.Windows"]

analysis = Analysis(
    [str(project_root / "src" / "caleo_transcriber" / "__main__.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=metadata,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "mypy", "ruff", "PySide6.QtWebEngineCore"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="CaleoTranscriber",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    version=str(project_root / "packaging" / "windows-version.txt"),
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="CaleoTranscriber",
)
