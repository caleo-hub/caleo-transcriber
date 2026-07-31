"""Regras e valores independentes de infraestrutura."""

from caleo_transcriber.domain.attempt import (
    ALLOWED_TRANSITIONS,
    AttemptState,
    InvalidAttemptTransition,
    can_transition,
    require_transition,
)
from caleo_transcriber.domain.long_media import (
    MAX_UPLOAD_BYTES,
    OVERLAP_MS,
    ChunkPlan,
    ChunkTranscript,
    InvalidChunkPlan,
    TimedText,
    merge_transcripts,
    plan_chunks,
    validate_plan,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "AttemptState",
    "ChunkPlan",
    "ChunkTranscript",
    "InvalidAttemptTransition",
    "InvalidChunkPlan",
    "MAX_UPLOAD_BYTES",
    "OVERLAP_MS",
    "TimedText",
    "can_transition",
    "merge_transcripts",
    "plan_chunks",
    "require_transition",
    "validate_plan",
]
