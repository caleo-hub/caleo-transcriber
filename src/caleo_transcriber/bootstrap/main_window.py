"""Composition root concreto do aplicativo desktop."""

import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QWidget

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.adapters.filesystem import AtomicTxtOutputWriter
from caleo_transcriber.adapters.media import FfmpegAudioExtractor, FfmpegMediaProbe, FfmpegTools
from caleo_transcriber.adapters.openai import OpenAISdkTransport, OpenAIWhisperAdapter
from caleo_transcriber.application import ApiKeySettings, TranscribeSingleFile
from caleo_transcriber.presentation import (
    MainWindow,
    QSettingsCloudNoticePolicy,
    QtAttemptEvents,
)
from caleo_transcriber.presentation.settings import ApiKeySettingsWidget


def _ffmpeg_tools() -> FfmpegTools:
    executable_root = Path(sys.executable).resolve().parent
    packaged = executable_root / "ffmpeg"
    if (packaged / "ffmpeg.exe").is_file() and (packaged / "ffprobe.exe").is_file():
        return FfmpegTools(packaged / "ffmpeg.exe", packaged / "ffprobe.exe")

    project_root = Path(__file__).resolve().parents[3]
    candidates = list((project_root / "vendor" / "ffmpeg" / "bin").glob("ffmpeg-8.1.2-lgpl/**/bin"))
    if len(candidates) == 1:
        return FfmpegTools(candidates[0] / "ffmpeg.exe", candidates[0] / "ffprobe.exe")
    return FfmpegTools(packaged / "ffmpeg.exe", packaged / "ffprobe.exe")


def create_main_window() -> MainWindow:
    credential_store = WindowsCredentialStore()
    tools = _ffmpeg_tools()
    events = QtAttemptEvents()
    use_case = TranscribeSingleFile(
        FfmpegMediaProbe(tools),
        FfmpegAudioExtractor(tools),
        OpenAIWhisperAdapter(credential_store, OpenAISdkTransport()),
        AtomicTxtOutputWriter(),
        events,
    )
    cache_root = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
    workspace = Path(cache_root) / "work"

    def settings_factory() -> QWidget:
        return ApiKeySettingsWidget(ApiKeySettings(credential_store))

    return MainWindow(
        use_case,
        events,
        workspace,
        settings_factory,
        QSettingsCloudNoticePolicy(),
    )
