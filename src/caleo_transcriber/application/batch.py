"""Scheduler FIFO em memória para o caso de uso de mídia longa."""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from threading import Event, RLock
from typing import Protocol, runtime_checkable

from caleo_transcriber.application.output import OutputFormat
from caleo_transcriber.application.transcribe_long_media import TranscribeLongMediaCommand
from caleo_transcriber.application.transcribe_single_file import (
    AttemptFailure,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
)
from caleo_transcriber.domain import BatchItem, BatchItemState, BatchQueue, BatchSummary


@dataclass(frozen=True, slots=True)
class BatchSettings:
    output_directory: Path
    workspace: Path
    output_format: OutputFormat
    language: str | None = None


@dataclass(frozen=True, slots=True)
class BatchAddResult:
    added_item_ids: tuple[str, ...]
    duplicate_count: int


@dataclass(frozen=True, slots=True)
class BatchQueueEvent:
    batch_id: str
    item_id: str
    position: int
    state: BatchItemState
    failure: str | None = None


@runtime_checkable
class BatchEvents(Protocol):
    def publish(self, event: BatchQueueEvent) -> None: ...


@runtime_checkable
class LongMediaUseCase(Protocol):
    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult: ...


class BatchProcessor:
    """Executa um item por vez e preserva cada estado terminal."""

    def __init__(
        self,
        use_case: LongMediaUseCase,
        settings: BatchSettings,
        events: BatchEvents,
        batch_id: str | None = None,
    ) -> None:
        self._use_case = use_case
        self._settings = settings
        self._events = events
        self._batch_id = batch_id or str(uuid.uuid4())
        self._queue = BatchQueue()
        self._sources: dict[str, Path] = {}
        self._results: dict[str, TranscribeSingleFileResult] = {}
        self._retry_ids: set[str] = set()
        self._confirm_ids: set[str] = set()
        self._active_cancel: Event | None = None
        self._active_id: str | None = None
        self._running = False
        self._lock = RLock()

    @property
    def items(self) -> tuple[BatchItem, ...]:
        with self._lock:
            return self._queue.items

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    def add_sources(self, sources: Iterable[Path]) -> BatchAddResult:
        added: list[str] = []
        duplicates = 0
        with self._lock:
            if self._running:
                raise RuntimeError("configuração do lote bloqueada durante execução")
            for source in sources:
                item_id = str(uuid.uuid4())
                identity = os.path.normcase(os.path.abspath(source))
                if not self._queue.add(item_id, identity):
                    duplicates += 1
                    continue
                self._sources[item_id] = source
                added.append(item_id)
                self._publish(self._queue.items[-1])
        return BatchAddResult(tuple(added), duplicates)

    def configure(self, settings: BatchSettings) -> None:
        with self._lock:
            if self._running:
                raise RuntimeError("configuração do lote bloqueada durante execução")
            self._settings = settings

    def run(self) -> BatchSummary:
        with self._lock:
            if self._running:
                raise RuntimeError("lote já está em execução")
            self._running = True
        try:
            while True:
                with self._lock:
                    item = self._queue.next_queued()
                    if item is None:
                        return self._queue.summary()
                    item = self._queue.set_state(item.item_id, BatchItemState.PREPARING)
                    cancel = Event()
                    self._active_id = item.item_id
                    self._active_cancel = cancel
                    self._publish(item)
                    source = self._sources[item.item_id]
                    retry_failed = item.item_id in self._retry_ids
                result = self._use_case.execute(
                    TranscribeLongMediaCommand(
                        attempt_id=item.item_id,
                        source=source,
                        output_directory=self._settings.output_directory,
                        workspace=self._settings.workspace,
                        output_format=self._settings.output_format,
                        language=self._settings.language,
                        retry_failed=retry_failed,
                        confirm_ambiguous=item.item_id in self._confirm_ids,
                    ),
                    cancel.is_set,
                )
                with self._lock:
                    self._results[item.item_id] = result
                    self._retry_ids.discard(item.item_id)
                    self._confirm_ids.discard(item.item_id)
                    current = next(
                        candidate
                        for candidate in self._queue.items
                        if candidate.item_id == item.item_id
                    )
                    if isinstance(result, TranscribeSingleFileFailure):
                        if (
                            result.category is AttemptFailure.CANCELLED
                            or current.state is BatchItemState.CANCELLING
                        ):
                            if current.state is not BatchItemState.CANCELLING:
                                current = self._queue.set_state(
                                    item.item_id, BatchItemState.CANCELLING
                                )
                                self._publish(current)
                            current = self._queue.set_state(item.item_id, BatchItemState.CANCELLED)
                        else:
                            failure = (
                                AttemptFailure.PROVIDER.value
                                if result.category is AttemptFailure.AMBIGUOUS
                                else result.category.value
                            )
                            current = self._queue.set_state(
                                item.item_id, BatchItemState.FAILED, failure
                            )
                    else:
                        current = self._queue.set_state(item.item_id, BatchItemState.COMPLETED)
                    self._publish(current)
                    self._active_id = None
                    self._active_cancel = None
        finally:
            with self._lock:
                self._running = False
                self._active_id = None
                self._active_cancel = None

    def cancel_item(self, item_id: str) -> bool:
        with self._lock:
            item = next((item for item in self._queue.items if item.item_id == item_id), None)
            if item is None:
                return False
            if item.state is BatchItemState.QUEUED:
                self._publish(self._queue.cancel_pending(item_id))
                return True
            if item.item_id == self._active_id and item.state in {
                BatchItemState.PREPARING,
                BatchItemState.TRANSCRIBING,
                BatchItemState.SAVING,
            }:
                updated = self._queue.set_state(item_id, BatchItemState.CANCELLING)
                self._publish(updated)
                if self._active_cancel is not None:
                    self._active_cancel.set()
                return True
            return False

    def cancel_all(self) -> None:
        with self._lock:
            for item in self._queue.cancel_all_pending():
                self._publish(item)
            if self._active_id is not None and self._active_cancel is not None:
                active = next(item for item in self._queue.items if item.item_id == self._active_id)
                if active.state is not BatchItemState.CANCELLING:
                    self._publish(self._queue.set_state(active.item_id, BatchItemState.CANCELLING))
                self._active_cancel.set()

    def retry_failed(self) -> tuple[str, ...]:
        with self._lock:
            retried = self._queue.retry_failed()
            ids = tuple(item.item_id for item in retried)
            self._retry_ids.update(ids)
            for item in retried:
                self._publish(item)
            return ids

    def retry_ambiguous(self, item_id: str) -> bool:
        with self._lock:
            result = self._results.get(item_id)
            if not isinstance(result, TranscribeSingleFileFailure) or (
                result.category is not AttemptFailure.AMBIGUOUS
            ):
                return False
            item = self._queue.retry_item(item_id)
            self._confirm_ids.add(item_id)
            self._publish(item)
            return True

    def result_for(self, item_id: str) -> TranscribeSingleFileResult | None:
        with self._lock:
            return self._results.get(item_id)

    def summary(self) -> BatchSummary:
        with self._lock:
            return self._queue.summary()

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()
            self._sources.clear()
            self._results.clear()
            self._retry_ids.clear()
            self._confirm_ids.clear()

    def _publish(self, item: BatchItem) -> None:
        self._events.publish(
            BatchQueueEvent(
                self._batch_id,
                item.item_id,
                item.position,
                item.state,
                item.failure,
            )
        )
