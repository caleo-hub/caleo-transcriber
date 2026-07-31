"""Agregado efêmero de fila FIFO, independente de UI e infraestrutura."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class BatchItemState(StrEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    TRANSCRIBING = "transcribing"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"


ACTIVE_BATCH_STATES = frozenset(
    {
        BatchItemState.PREPARING,
        BatchItemState.TRANSCRIBING,
        BatchItemState.SAVING,
        BatchItemState.CANCELLING,
    }
)
TERMINAL_BATCH_STATES = frozenset(
    {BatchItemState.COMPLETED, BatchItemState.FAILED, BatchItemState.CANCELLED}
)


@dataclass(frozen=True, slots=True)
class BatchItem:
    item_id: str
    source_identity: str
    position: int
    state: BatchItemState = BatchItemState.QUEUED
    attempts: int = 1
    failure: str | None = None


@dataclass(frozen=True, slots=True)
class BatchSummary:
    total: int
    terminal: int
    completed: int
    failed: int
    cancelled: int


class BatchQueueError(RuntimeError):
    pass


class BatchQueue:
    def __init__(self) -> None:
        self._items: list[BatchItem] = []

    @property
    def items(self) -> tuple[BatchItem, ...]:
        return tuple(self._items)

    def add(self, item_id: str, source_identity: str) -> bool:
        if any(item.source_identity == source_identity for item in self._items):
            return False
        self._items.append(BatchItem(item_id, source_identity, len(self._items)))
        return True

    def next_queued(self) -> BatchItem | None:
        return next((item for item in self._items if item.state is BatchItemState.QUEUED), None)

    def set_state(
        self, item_id: str, state: BatchItemState, failure: str | None = None
    ) -> BatchItem:
        index, current = self._find(item_id)
        if state in ACTIVE_BATCH_STATES and any(
            item.item_id != item_id and item.state in ACTIVE_BATCH_STATES for item in self._items
        ):
            raise BatchQueueError("somente um item pode estar ativo")
        if not _can_transition(current.state, state):
            raise BatchQueueError("transição de fila inválida")
        if state is BatchItemState.FAILED and failure is None:
            raise BatchQueueError("falha terminal exige categoria")
        if state is not BatchItemState.FAILED and failure is not None:
            raise BatchQueueError("categoria só é aceita para falha")
        updated = replace(current, state=state, failure=failure)
        self._items[index] = updated
        return updated

    def cancel_pending(self, item_id: str) -> BatchItem:
        return self.set_state(item_id, BatchItemState.CANCELLED)

    def cancel_all_pending(self) -> tuple[BatchItem, ...]:
        changed: list[BatchItem] = []
        for item in tuple(self._items):
            if item.state is BatchItemState.QUEUED:
                changed.append(self.cancel_pending(item.item_id))
        return tuple(changed)

    def retry_failed(self) -> tuple[BatchItem, ...]:
        if any(item.state in ACTIVE_BATCH_STATES for item in self._items):
            raise BatchQueueError("não é possível repetir durante processamento")
        retried: list[BatchItem] = []
        for index, item in enumerate(self._items):
            if item.state is BatchItemState.FAILED:
                updated = replace(
                    item,
                    state=BatchItemState.QUEUED,
                    attempts=item.attempts + 1,
                    failure=None,
                )
                self._items[index] = updated
                retried.append(updated)
        return tuple(retried)

    def retry_item(self, item_id: str) -> BatchItem:
        index, item = self._find(item_id)
        if item.state is not BatchItemState.FAILED:
            raise BatchQueueError("somente falha pode ser repetida")
        updated = replace(
            item,
            state=BatchItemState.QUEUED,
            attempts=item.attempts + 1,
            failure=None,
        )
        self._items[index] = updated
        return updated

    def summary(self) -> BatchSummary:
        states = [item.state for item in self._items]
        return BatchSummary(
            total=len(states),
            terminal=sum(state in TERMINAL_BATCH_STATES for state in states),
            completed=states.count(BatchItemState.COMPLETED),
            failed=states.count(BatchItemState.FAILED),
            cancelled=states.count(BatchItemState.CANCELLED),
        )

    def clear(self) -> None:
        if any(item.state in ACTIVE_BATCH_STATES for item in self._items):
            raise BatchQueueError("não é possível limpar item ativo")
        self._items.clear()

    def _find(self, item_id: str) -> tuple[int, BatchItem]:
        for index, item in enumerate(self._items):
            if item.item_id == item_id:
                return index, item
        raise BatchQueueError("item inexistente")


def _can_transition(current: BatchItemState, target: BatchItemState) -> bool:
    allowed = {
        BatchItemState.QUEUED: {BatchItemState.PREPARING, BatchItemState.CANCELLED},
        BatchItemState.PREPARING: {
            BatchItemState.TRANSCRIBING,
            BatchItemState.COMPLETED,
            BatchItemState.FAILED,
            BatchItemState.CANCELLING,
            BatchItemState.CANCELLED,
        },
        BatchItemState.TRANSCRIBING: {
            BatchItemState.SAVING,
            BatchItemState.FAILED,
            BatchItemState.CANCELLING,
            BatchItemState.CANCELLED,
        },
        BatchItemState.SAVING: {
            BatchItemState.COMPLETED,
            BatchItemState.FAILED,
            BatchItemState.CANCELLING,
            BatchItemState.CANCELLED,
        },
        BatchItemState.CANCELLING: {BatchItemState.CANCELLED},
        BatchItemState.COMPLETED: set(),
        BatchItemState.FAILED: {BatchItemState.QUEUED},
        BatchItemState.CANCELLED: set(),
    }
    return target in allowed[current]
