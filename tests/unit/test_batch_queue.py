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
