"""Composition root concreto do aplicativo desktop."""

import sys
from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QWidget

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.adapters.filesystem import (
    AtomicTranscriptOutputWriter,
    DpapiProtector,
    WindowsCheckpointStore,
    fingerprint_source,
    hash_parameters,
)
from caleo_transcriber.adapters.media import (
    FfmpegAudioExtractor,
    FfmpegChunkAudioExtractor,
    FfmpegMediaProbe,
    FfmpegSilenceDetector,
    FfmpegTools,
)
from caleo_transcriber.adapters.openai import OpenAISdkTransport, OpenAIWhisperAdapter
from caleo_transcriber.application import (
    ApiKeySettings,
    AttemptEvent,
    BatchProcessor,
    BatchSettings,
    OutputFormat,
    TranscribeLongMedia,
)
from caleo_transcriber.presentation import (
    MainWindow,
    QSettingsCloudNoticePolicy,
    QtBatchEvents,
)
from caleo_transcriber.presentation.settings import ApiKeySettingsWidget


def _ffmpeg_tools() -> FfmpegTools:
    executable_root = Path(sys.executable).resolve().parent
    bundle_root = Path(getattr(sys, "_MEIPASS", executable_root))
    packaged_roots = (executable_root / "ffmpeg", bundle_root / "ffmpeg")
    for packaged in packaged_roots:
        if (packaged / "ffmpeg.exe").is_file() and (packaged / "ffprobe.exe").is_file():
            return FfmpegTools(packaged / "ffmpeg.exe", packaged / "ffprobe.exe")

    project_root = Path(__file__).resolve().parents[3]
    candidates = list((project_root / "vendor" / "ffmpeg" / "bin").glob("ffmpeg-8.1.2-lgpl/**/bin"))
    if len(candidates) == 1:
        return FfmpegTools(candidates[0] / "ffmpeg.exe", candidates[0] / "ffprobe.exe")
    fallback = executable_root / "ffmpeg"
    return FfmpegTools(fallback / "ffmpeg.exe", fallback / "ffprobe.exe")


def create_main_window() -> MainWindow:
    credential_store = WindowsCredentialStore()
    tools = _ffmpeg_tools()
    cache_root = Path(
        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation)
    )
    workspace = cache_root / "work"
    attempt_events = _NullAttemptEvents()
    use_case = TranscribeLongMedia(
        FfmpegMediaProbe(tools),
        FfmpegAudioExtractor(tools),
        FfmpegChunkAudioExtractor(tools),
        FfmpegSilenceDetector(tools),
        OpenAIWhisperAdapter(credential_store, OpenAISdkTransport()),
        WindowsCheckpointStore(cache_root / "checkpoints", DpapiProtector()),
        AtomicTranscriptOutputWriter(),
        attempt_events,
        fingerprint_source,
        hash_parameters,
        lambda: datetime.now(UTC),
    )
    events = QtBatchEvents()
    processor = BatchProcessor(
        use_case,
        BatchSettings(cache_root, workspace, OutputFormat.TXT),
        events,
    )

    def settings_factory() -> QWidget:
        return ApiKeySettingsWidget(ApiKeySettings(credential_store))

    return MainWindow(
        processor,
        events,
        workspace,
        settings_factory,
        QSettingsCloudNoticePolicy(),
    )


class _NullAttemptEvents:
    def publish(self, event: AttemptEvent) -> None:
        return None
