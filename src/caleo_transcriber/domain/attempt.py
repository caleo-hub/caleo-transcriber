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


class InvalidAttemptTransition(RuntimeError):
    """Indica violação da máquina de estados aprovada."""

    def __init__(self, current: AttemptState, target: AttemptState) -> None:
        self.current = current
        self.target = target
        super().__init__("Invalid attempt state transition")


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


def require_transition(current: AttemptState, target: AttemptState) -> AttemptState:
    """Valida e retorna o próximo estado sem produzir efeitos externos."""
    if not can_transition(current, target):
        raise InvalidAttemptTransition(current, target)
    return target
