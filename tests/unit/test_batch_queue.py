import pytest

from caleo_transcriber.domain import (
    BatchItemState,
    BatchQueue,
    BatchQueueError,
)


def test_fifo_deduplicates_and_reports_count_summary() -> None:
    queue = BatchQueue()

    assert queue.add("a", "same") is True
    assert queue.add("duplicate", "same") is False
    assert queue.add("b", "other") is True
    assert queue.next_queued() is not None
    assert queue.next_queued().item_id == "a"  # type: ignore[union-attr]
    queue.set_state("a", BatchItemState.PREPARING)
    queue.set_state("a", BatchItemState.COMPLETED)

    assert queue.next_queued().item_id == "b"  # type: ignore[union-attr]
    assert queue.summary().terminal == 1
    assert queue.summary().total == 2


def test_queue_never_allows_two_active_items() -> None:
    queue = BatchQueue()
    queue.add("a", "one")
    queue.add("b", "two")
    queue.set_state("a", BatchItemState.PREPARING)

    with pytest.raises(BatchQueueError, match="somente um"):
        queue.set_state("b", BatchItemState.PREPARING)


def test_retry_only_failed_preserves_completed_and_order() -> None:
    queue = BatchQueue()
    for item_id in ("a", "b", "c"):
        queue.add(item_id, item_id)
    queue.set_state("a", BatchItemState.PREPARING)
    queue.set_state("a", BatchItemState.COMPLETED)
    queue.set_state("b", BatchItemState.PREPARING)
    queue.set_state("b", BatchItemState.FAILED, "network")
    queue.cancel_pending("c")

    retried = queue.retry_failed()

    assert [item.item_id for item in retried] == ["b"]
    assert [item.state for item in queue.items] == [
        BatchItemState.COMPLETED,
        BatchItemState.QUEUED,
        BatchItemState.CANCELLED,
    ]
    assert queue.items[1].attempts == 2


def test_move_selected_queued_preserves_terminal_slots_and_selection_order() -> None:
    queue = BatchQueue()
    for item_id in ("done", "first", "second", "third"):
        queue.add(item_id, item_id)
    queue.set_state("done", BatchItemState.PREPARING)
    queue.set_state("done", BatchItemState.COMPLETED)

    moved = queue.move_queued(("second", "third"), -1)

    assert [item.item_id for item in queue.items] == ["done", "second", "third", "first"]
    assert [item.item_id for item in moved] == ["second", "third"]
    assert [item.position for item in queue.items] == [0, 1, 2, 3]


def test_remove_and_clear_never_remove_active_item() -> None:
    queue = BatchQueue()
    for item_id in ("active", "pending", "failed"):
        queue.add(item_id, item_id)
    queue.set_state("active", BatchItemState.PREPARING)
    queue.cancel_pending("failed")

    removed = queue.remove(("active", "pending"))
    cleared = queue.clear_inactive()

    assert [item.item_id for item in removed] == ["pending"]
    assert [item.item_id for item in cleared] == ["failed"]
    assert [item.item_id for item in queue.items] == ["active"]


def test_retry_selected_ignores_non_failed_items() -> None:
    queue = BatchQueue()
    for item_id in ("done", "failed", "cancelled"):
        queue.add(item_id, item_id)
    queue.set_state("done", BatchItemState.PREPARING)
    queue.set_state("done", BatchItemState.COMPLETED)
    queue.set_state("failed", BatchItemState.PREPARING)
    queue.set_state("failed", BatchItemState.FAILED, "network")
    queue.cancel_pending("cancelled")

    retried = queue.retry_items(("done", "failed", "cancelled"))

    assert [item.item_id for item in retried] == ["failed"]
    assert queue.items[1].state is BatchItemState.QUEUED
