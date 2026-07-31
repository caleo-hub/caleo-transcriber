"""Probe e extração segura com os executáveis FFmpeg aprovados."""

import json
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Self

from caleo_transcriber.application.media import MediaError, MediaFailure, MediaInfo, PreparedAudio

MAX_DURATION_SECONDS = 30 * 60
MAX_PROVIDER_BYTES = 25_000_000
SUPPORTED_FORMATS = {
    ".mp3": {"mp3"},
    ".wav": {"wav"},
    ".mp4": {"mov", "mp4", "m4a", "3gp", "3g2", "mj2"},
}


@dataclass(frozen=True, slots=True)
class FfmpegTools:
    ffmpeg: Path
    ffprobe: Path


class FfmpegMediaProbe:
    def __init__(self, tools: FfmpegTools, timeout_seconds: float = 15.0) -> None:
        self._tools = tools
        self._timeout_seconds = timeout_seconds

    def probe(self, source: Path) -> MediaInfo:
        try:
            resolved = source.resolve(strict=True)
        except OSError as error:
            raise MediaError(MediaFailure.MISSING) from error
        if not resolved.is_file():
            raise MediaError(MediaFailure.MISSING)
        if resolved.suffix.lower() not in SUPPORTED_FORMATS:
            raise MediaError(MediaFailure.UNSUPPORTED)
        if resolved.stat().st_size == 0:
            raise MediaError(MediaFailure.EMPTY)

        args = [
            str(self._tools.ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration,format_name:stream=codec_type",
            "-of",
            "json",
            str(resolved),
        ]
        try:
            completed = subprocess.run(  # noqa: S603 - lista de argumentos, sem shell
                args,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            raise MediaError(MediaFailure.TIMEOUT) from error
        except OSError as error:
            raise MediaError(MediaFailure.PROCESSING) from error
        if completed.returncode != 0:
            raise MediaError(MediaFailure.CORRUPT)

        try:
            payload = json.loads(completed.stdout)
            format_name = str(payload["format"]["format_name"])
            duration = float(payload["format"]["duration"])
            stream_types = {str(stream["codec_type"]) for stream in payload.get("streams", [])}
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise MediaError(MediaFailure.CORRUPT) from error

        expected_formats = SUPPORTED_FORMATS[resolved.suffix.lower()]
        if not expected_formats.intersection(format_name.split(",")):
            raise MediaError(MediaFailure.UNSUPPORTED)
        if "audio" not in stream_types:
            raise MediaError(MediaFailure.NO_AUDIO)
        if duration <= 0:
            raise MediaError(MediaFailure.INVALID_DURATION)
        if duration > MAX_DURATION_SECONDS:
            raise MediaError(MediaFailure.DURATION_LIMIT)
        return MediaInfo(
            duration_seconds=duration,
            format_name=format_name,
            has_audio=True,
            has_video="video" in stream_types,
        )


class FfmpegAudioExtractor:
    def __init__(self, tools: FfmpegTools, timeout_seconds: float = 30 * 60) -> None:
        self._tools = tools
        self._timeout_seconds = timeout_seconds

    def prepare(
        self,
        source: Path,
        info: MediaInfo,
        workspace: Path,
        should_cancel: Callable[[], bool] | None = None,
    ) -> "FfmpegPreparedAudioLease":
        return FfmpegPreparedAudioLease(
            self._tools,
            source,
            info,
            workspace,
            should_cancel or (lambda: False),
            self._timeout_seconds,
        )


class FfmpegPreparedAudioLease:
    def __init__(
        self,
        tools: FfmpegTools,
        source: Path,
        info: MediaInfo,
        workspace: Path,
        should_cancel: Callable[[], bool],
        timeout_seconds: float,
    ) -> None:
        self._tools = tools
        self._source = source
        self._info = info
        self._workspace = workspace
        self._should_cancel = should_cancel
        self._timeout_seconds = timeout_seconds
        self._temporary_directory: Path | None = None
        self._audio: PreparedAudio | None = None

    @property
    def audio(self) -> PreparedAudio:
        if self._audio is None:
            raise RuntimeError("Prepared audio is only available inside its lease.")
        return self._audio

    def __enter__(self) -> Self:
        if self._should_cancel():
            raise MediaError(MediaFailure.CANCELLED)
        self._workspace.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix="caleo-", dir=self._workspace))
        self._temporary_directory = temporary
        output = temporary / "audio.mp3"
        args = [
            str(self._tools.ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-i",
            str(self._source.resolve()),
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "64k",
            str(output),
        ]
        try:
            self._run(args)
            size = output.stat().st_size
            if size <= 0:
                raise MediaError(MediaFailure.PROCESSING)
            if size >= MAX_PROVIDER_BYTES:
                raise MediaError(MediaFailure.PROVIDER_LIMIT)
            self._audio = PreparedAudio(output, self._info.duration_seconds, size)
            return self
        except BaseException:
            self._cleanup()
            raise

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._cleanup()

    def _run(self, args: list[str]) -> None:
        creation_flags = (
            subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        try:
            process = subprocess.Popen(  # noqa: S603 - lista de argumentos, sem shell
                args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                creationflags=creation_flags,
            )
        except OSError as error:
            raise MediaError(MediaFailure.PROCESSING) from error

        deadline = time.monotonic() + self._timeout_seconds
        while True:
            if self._should_cancel():
                self._stop(process)
                raise MediaError(MediaFailure.CANCELLED)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self._stop(process)
                raise MediaError(MediaFailure.TIMEOUT)
            try:
                _, _ = process.communicate(timeout=min(0.1, remaining))
                break
            except subprocess.TimeoutExpired:
                continue
        if process.returncode != 0:
            raise MediaError(MediaFailure.PROCESSING)

    @staticmethod
    def _stop(process: subprocess.Popen[str]) -> None:
        process.terminate()
        try:
            process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()

    def _cleanup(self) -> None:
        self._audio = None
        if self._temporary_directory is not None:
            shutil.rmtree(self._temporary_directory, ignore_errors=True)
            self._temporary_directory = None
