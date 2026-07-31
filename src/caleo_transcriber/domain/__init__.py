"""Regras e valores independentes de infraestrutura."""

from caleo_transcriber.domain.attempt import (
    ALLOWED_TRANSITIONS,
    AttemptState,
    InvalidAttemptTransition,
    can_transition,
    require_transition,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "AttemptState",
    "InvalidAttemptTransition",
    "can_transition",
    "require_transition",
]
