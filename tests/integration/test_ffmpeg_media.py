import json
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from caleo_transcriber.adapters.media import FfmpegAudioExtractor, FfmpegMediaProbe, FfmpegTools
from caleo_transcriber.application import MediaError, MediaFailure, MediaProbe, PreparedAudioLease

pytestmark = pytest.mark.integration


def _tools() -> FfmpegTools:
    roots = list(Path("vendor/ffmpeg/bin").glob("ffmpeg-8.1.2-lgpl/**/bin"))
    if len(roots) != 1:
        pytest.skip("build FFmpeg aprovado não está disponível")
    return FfmpegTools(roots[0] / "ffmpeg.exe", roots[0] / "ffprobe.exe")


def _run(args: list[str]) -> None:
    subprocess.run(  # noqa: S603 - gerador usa argumentos controlados e sem shell
        args, check=True, capture_output=True, shell=False, timeout=30
    )


@pytest.fixture
def synthetic_media(tmp_path: Path) -> Iterator[dict[str, Path]]:
    tools = _tools()
    wav = tmp_path / "áudio [teste] !.wav"
    mp3 = tmp_path / "áudio [teste] !.mp3"
    mp4 = tmp_path / "vídeo [teste] !.mp4"
    video_only = tmp_path / "sem áudio.mp4"
    base = [str(tools.ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    _run([*base, "-f", "lavfi", "-i", "sine=frequency=1000:duration=1", str(wav)])
    _run(
        [
            *base,
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=1",
            "-codec:a",
            "libmp3lame",
            str(mp3),
        ]
    )
    _run(
        [
            *base,
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=160x120:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:duration=1",
            "-shortest",
            "-codec:v",
            "mpeg4",
            "-codec:a",
            "aac",
            str(mp4),
        ]
    )
    _run(
        [
            *base,
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=160x120:d=1",
            "-codec:v",
            "mpeg4",
            str(video_only),
        ]
    )
    yield {"wav": wav, "mp3": mp3, "mp4": mp4, "video_only": video_only}


def test_probe_accepts_supported_synthetic_media(synthetic_media: dict[str, Path]) -> None:
    probe = FfmpegMediaProbe(_tools())

    assert isinstance(probe, MediaProbe)
    assert probe.probe(synthetic_media["wav"]).has_video is False
    assert probe.probe(synthetic_media["mp3"]).has_video is False
    assert probe.probe(synthetic_media["mp4"]).has_video is True


def test_probe_rejects_empty_corrupt_unsupported_and_video_only(
    synthetic_media: dict[str, Path], tmp_path: Path
) -> None:
    probe = FfmpegMediaProbe(_tools())
    cases = {
        tmp_path / "empty.wav": MediaFailure.EMPTY,
        tmp_path / "corrupt.mp3": MediaFailure.CORRUPT,
        tmp_path / "unsupported.ogg": MediaFailure.UNSUPPORTED,
        synthetic_media["video_only"]: MediaFailure.NO_AUDIO,
    }
    (tmp_path / "empty.wav").touch()
    (tmp_path / "corrupt.mp3").write_bytes(b"not-media")
    (tmp_path / "unsupported.ogg").write_bytes(b"not-media")

    for source, reason in cases.items():
        with pytest.raises(MediaError) as caught:
            probe.probe(source)
        assert caught.value.reason is reason


def test_mp4_preparation_contains_only_small_mono_audio_and_cleans_up(
    synthetic_media: dict[str, Path], tmp_path: Path
) -> None:
    tools = _tools()
    info = FfmpegMediaProbe(tools).probe(synthetic_media["mp4"])
    lease = FfmpegAudioExtractor(tools).prepare(
        synthetic_media["mp4"], info, tmp_path / "workspace"
    )

    assert isinstance(lease, PreparedAudioLease)
    with lease:
        output = lease.audio.path
        assert output.exists()
        assert output.stat().st_size < 25_000_000
        completed = subprocess.run(  # noqa: S603 - teste usa executável aprovado e argumentos fixos
            [
                str(tools.ffprobe),
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,channels",
                "-of",
                "json",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
            shell=False,
            timeout=15,
        )
        streams = json.loads(completed.stdout)["streams"]
        assert streams == [{"codec_type": "audio", "channels": 1}]

    assert output.exists() is False
    assert list((tmp_path / "workspace").iterdir()) == []


def test_cancelled_preparation_has_no_residue(
    synthetic_media: dict[str, Path], tmp_path: Path
) -> None:
    tools = _tools()
    info = FfmpegMediaProbe(tools).probe(synthetic_media["wav"])
    workspace = tmp_path / "workspace"

    with pytest.raises(MediaError) as caught:
        with FfmpegAudioExtractor(tools).prepare(
            synthetic_media["wav"], info, workspace, lambda: True
        ):
            pass

    assert caught.value.reason is MediaFailure.CANCELLED
    assert workspace.exists() is False or list(workspace.iterdir()) == []
