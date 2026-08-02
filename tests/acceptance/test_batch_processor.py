from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event, Thread

from caleo_transcriber.application import (
    AttemptFailure,
    BatchProcessor,
    BatchQueueEvent,
    BatchSettings,
    OutputFormat,
    TranscribeLongMediaCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
    TranscribeSingleFileSuccess,
)
from caleo_transcriber.domain import AttemptState, BatchItemState


class RecordingBatchEvents:
    def __init__(self) -> None:
        self.events: list[BatchQueueEvent] = []

    def publish(self, event: BatchQueueEvent) -> None:
        self.events.append(event)


class FakeLongMediaUseCase:
    def __init__(self, results: list[TranscribeSingleFileResult]) -> None:
        self.results = results
        self.calls: list[TranscribeLongMediaCommand] = []
        self.max_active = 0
        self._active = 0

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        self._active += 1
        self.max_active = max(self.max_active, self._active)
        try:
            return self.results.pop(0)
        finally:
            self._active -= 1


class BlockingCancelledUseCase(FakeLongMediaUseCase):
    def __init__(self) -> None:
        super().__init__([])
        self.entered = Event()

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        self.entered.set()
        assert should_cancel is not None
        assert Event().wait(0.01) is False
        while not should_cancel():
            Event().wait(0.001)
        return _failure(AttemptFailure.CANCELLED)


class PausableUseCase(FakeLongMediaUseCase):
    def __init__(self) -> None:
        super().__init__([_success("second")])
        self.entered = Event()
        self.release = Event()

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        if len(self.calls) == 1:
            self.entered.set()
            assert self.release.wait(timeout=2)
            return _success("first")
        return self.results.pop(0)


class CancelCurrentThenSuccessUseCase(FakeLongMediaUseCase):
    def __init__(self) -> None:
        super().__init__([])
        self.entered = Event()

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        if len(self.calls) == 1:
            self.entered.set()
            assert should_cancel is not None
            while not should_cancel():
                Event().wait(0.001)
            return _failure(AttemptFailure.CANCELLED)
        return _success("pending")


def _success(name: str) -> TranscribeSingleFileSuccess:
    return TranscribeSingleFileSuccess(name, Path(f"C:/out/{name}.txt"), (), AttemptState.COMPLETED)


def _failure(category: AttemptFailure = AttemptFailure.NETWORK) -> TranscribeSingleFileFailure:
    state = AttemptState.CANCELLED if category is AttemptFailure.CANCELLED else AttemptState.FAILED
    return TranscribeSingleFileFailure("attempt", category, True, "safe", "SAFE", state)


def _processor(
    use_case: FakeLongMediaUseCase,
) -> tuple[BatchProcessor, RecordingBatchEvents]:
    events = RecordingBatchEvents()
    processor = BatchProcessor(
        use_case,
        BatchSettings(Path("C:/out"), Path("C:/cache"), OutputFormat.TXT),
        events,
        "batch-1",
    )
    return processor, events


def test_fifo_duplicate_and_failure_isolation_continue_to_next_item() -> None:
    use_case = FakeLongMediaUseCase([_success("one"), _failure(), _success("three")])
    processor, _ = _processor(use_case)
    added = processor.add_sources(
        [Path("one.mp4"), Path("two.wav"), Path("one.mp4"), Path("three.mp3")]
    )

    summary = processor.run()

    assert added.duplicate_count == 1
    assert [call.source.name for call in use_case.calls] == ["one.mp4", "two.wav", "three.mp3"]
    assert use_case.max_active == 1
    assert summary.total == 3
    assert summary.completed == 2
    assert summary.failed == 1


def test_source_folder_output_uses_each_source_directory_and_suffix() -> None:
    use_case = FakeLongMediaUseCase([_success("one"), _success("two")])
    events = RecordingBatchEvents()
    processor = BatchProcessor(
        use_case,
        BatchSettings(
            Path("C:/fallback"),
            Path("C:/cache"),
            OutputFormat.TXT,
            save_next_to_source=True,
        ),
        events,
        "batch-source-folder",
    )
    processor.add_sources([Path("C:/videos/a/one.mp4"), Path("D:/audio/b/two.wav")])

    summary = processor.run()

    assert summary.completed == 2
    assert [(call.output_directory, call.output_name_suffix) for call in use_case.calls] == [
        (Path("C:/videos/a"), "_transcription"),
        (Path("D:/audio/b"), "_transcription"),
    ]


def test_cancel_pending_has_no_use_case_call_and_retry_sends_only_failure() -> None:
    use_case = FakeLongMediaUseCase([_failure(), _success("second")])
    processor, _ = _processor(use_case)
    ids = processor.add_sources([Path("first.mp4"), Path("second.mp4")]).added_item_ids
    assert processor.cancel_item(ids[1]) is True

    processor.run()
    assert [call.source.name for call in use_case.calls] == ["first.mp4"]
    assert processor.retry_failed() == (ids[0],)
    summary = processor.run()

    assert [call.source.name for call in use_case.calls] == ["first.mp4", "first.mp4"]
    assert use_case.calls[-1].retry_failed is True
    assert summary.completed == 1
    assert summary.cancelled == 1


def test_cancel_active_and_all_pending_finish_without_starting_next() -> None:
    use_case = BlockingCancelledUseCase()
    processor, _ = _processor(use_case)
    ids = processor.add_sources([Path("active.mp4"), Path("pending.mp4")]).added_item_ids
    thread = Thread(target=processor.run)
    thread.start()
    assert use_case.entered.wait(timeout=2)

    processor.cancel_all()
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert len(use_case.calls) == 1
    assert [item.state for item in processor.items] == [
        BatchItemState.CANCELLED,
        BatchItemState.CANCELLED,
    ]
    assert processor.cancel_item(ids[0]) is False


def test_new_processor_has_empty_ephemeral_queue() -> None:
    first, _ = _processor(FakeLongMediaUseCase([]))
    first.add_sources([Path("one.mp4")])

    fresh, _ = _processor(FakeLongMediaUseCase([]))

    assert fresh.items == ()
    assert fresh.summary().total == 0


def test_reordered_pending_items_define_next_processing_order() -> None:
    use_case = FakeLongMediaUseCase([_success("three"), _success("one"), _success("two")])
    processor, _ = _processor(use_case)
    ids = processor.add_sources(
        [Path("one.mp4"), Path("two.mp4"), Path("three.mp4")]
    ).added_item_ids

    processor.move_items((ids[2],), -1)
    processor.move_items((ids[2],), -1)
    processor.run()

    assert [call.source.name for call in use_case.calls] == [
        "three.mp4",
        "one.mp4",
        "two.mp4",
    ]


def test_pause_after_current_preserves_pending_for_later_resume() -> None:
    use_case = PausableUseCase()
    processor, _ = _processor(use_case)
    processor.add_sources([Path("first.mp4"), Path("second.mp4")])
    thread = Thread(target=processor.run)
    thread.start()
    assert use_case.entered.wait(timeout=2)

    assert processor.pause_after_current() is True
    use_case.release.set()
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert len(use_case.calls) == 1
    assert [item.state for item in processor.items] == [
        BatchItemState.COMPLETED,
        BatchItemState.QUEUED,
    ]
    processor.run()
    assert len(use_case.calls) == 2


def test_cancel_active_does_not_cancel_pending_and_scheduler_continues() -> None:
    use_case = CancelCurrentThenSuccessUseCase()
    processor, _ = _processor(use_case)
    processor.add_sources([Path("active.mp4"), Path("pending.mp4")])
    thread = Thread(target=processor.run)
    thread.start()
    assert use_case.entered.wait(timeout=2)

    assert processor.cancel_active() is True
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert [call.source.name for call in use_case.calls] == ["active.mp4", "pending.mp4"]
    assert [item.state for item in processor.items] == [
        BatchItemState.CANCELLED,
        BatchItemState.COMPLETED,
    ]


def test_remove_and_clear_only_forget_queue_metadata() -> None:
    use_case = FakeLongMediaUseCase([])
    processor, _ = _processor(use_case)
    ids = processor.add_sources(
        [Path("one.mp4"), Path("two.mp4"), Path("three.mp4")]
    ).added_item_ids

    assert processor.remove_items((ids[1],)) == (ids[1],)
    assert processor.clear_pending() == (ids[0], ids[2])
    assert processor.items == ()
    assert use_case.calls == []
