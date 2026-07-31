"""Adapters de mídia baseados em FFmpeg."""

from .ffmpeg import (
    FfmpegAudioExtractor,
    FfmpegChunkAudioExtractor,
    FfmpegMediaProbe,
    FfmpegSilenceDetector,
    FfmpegTools,
)

__all__ = [
    "FfmpegAudioExtractor",
    "FfmpegChunkAudioExtractor",
    "FfmpegMediaProbe",
    "FfmpegSilenceDetector",
    "FfmpegTools",
]
