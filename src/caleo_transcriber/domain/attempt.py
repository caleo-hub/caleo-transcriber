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
