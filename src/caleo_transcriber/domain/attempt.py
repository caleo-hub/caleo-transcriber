"""Estado mínimo que torna o scaffold verificável."""

from enum import StrEnum


class AttemptState(StrEnum):
    READY = "ready"
    PREPARING = "preparing"
    TRANSCRIBING = "transcribing"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[AttemptState, frozenset[AttemptState]] = {
    AttemptState.READY: frozenset({AttemptState.PREPARING}),
    AttemptState.PREPARING: frozenset(
        {AttemptState.TRANSCRIBING, AttemptState.FAILED, AttemptState.CANCELLING}
    ),
    AttemptState.TRANSCRIBING: frozenset(
        {AttemptState.SAVING, AttemptState.FAILED, AttemptState.CANCELLING}
    ),
    AttemptState.SAVING: frozenset(
        {AttemptState.COMPLETED, AttemptState.FAILED, AttemptState.CANCELLING}
    ),
    AttemptState.CANCELLING: frozenset({AttemptState.CANCELLED}),
    AttemptState.COMPLETED: frozenset(),
    AttemptState.FAILED: frozenset(),
    AttemptState.CANCELLED: frozenset(),
}


def can_transition(current: AttemptState, target: AttemptState) -> bool:
    """Return whether the approved state machine permits a transition."""
    return target in ALLOWED_TRANSITIONS[current]
