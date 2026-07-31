"""Adapters de filesystem."""

from .atomic_transcript import AtomicTranscriptOutputWriter, render_srt, render_txt
from .atomic_txt import AtomicTxtOutputWriter, sanitize_output_stem
from .checkpoints import (
    CheckpointCorrupt,
    CheckpointError,
    DpapiProtector,
    WindowsCheckpointStore,
    fingerprint_source,
    hash_parameters,
)

__all__ = [
    "AtomicTxtOutputWriter",
    "AtomicTranscriptOutputWriter",
    "CheckpointCorrupt",
    "CheckpointError",
    "DpapiProtector",
    "WindowsCheckpointStore",
    "fingerprint_source",
    "hash_parameters",
    "render_srt",
    "render_txt",
    "sanitize_output_stem",
]
