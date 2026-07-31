import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from caleo_transcriber.adapters.media import FfmpegMediaProbe, FfmpegTools
from caleo_transcriber.application import MediaError, MediaFailure


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "synthetic.wav"
    source.write_bytes(b"fixture")
    return source


def _tools() -> FfmpegTools:
    return FfmpegTools(Path("ffmpeg.exe"), Path("ffprobe.exe"))


def test_probe_rejects_duration_above_thirty_minutes(tmp_path: Path) -> None:
    payload = {
        "format": {"format_name": "wav", "duration": "1800.001"},
        "streams": [{"codec_type": "audio"}],
    }
    completed = subprocess.CompletedProcess([], 0, json.dumps(payload), "")

    with patch("subprocess.run", return_value=completed):
        with pytest.raises(MediaError) as caught:
            FfmpegMediaProbe(_tools()).probe(_source(tmp_path))

    assert caught.value.reason is MediaFailure.DURATION_LIMIT


def test_probe_maps_timeout_without_exposing_path(tmp_path: Path) -> None:
    source = _source(tmp_path)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["ffprobe"], 1)):
        with pytest.raises(MediaError) as caught:
            FfmpegMediaProbe(_tools()).probe(source)

    assert caught.value.reason is MediaFailure.TIMEOUT
    assert source.name not in str(caught.value)
