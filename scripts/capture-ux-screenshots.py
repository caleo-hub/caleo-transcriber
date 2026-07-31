"""Gera evidências visuais determinísticas do gate UX sem rede ou mídia."""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from pathlib import Path
from threading import Event

from PySide6.QtWidgets import QApplication, QWidget

from caleo_transcriber.application import (
    AttemptFailure,
    BatchProcessor,
    BatchSettings,
    OutputFormat,
    TranscribeLongMediaCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
    TranscribeSingleFileSuccess,
)
from caleo_transcriber.domain import AttemptState
from caleo_transcriber.presentation import MainWindow, QtBatchEvents

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "evidence" / "ux-increment-2"


class _Notice:
    def should_show(self) -> bool:
        return False

    def mark_shown(self) -> None:
        return None


class _UseCase:
    def __init__(
        self, results: list[TranscribeSingleFileResult], release: Event | None = None
    ) -> None:
        self._results = results
        self._release = release
        self.entered = Event()

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.entered.set()
        if self._release is not None:
            while not self._release.wait(0.01):
                if should_cancel is not None and should_cancel():
                    return _failure(AttemptFailure.CANCELLED)
        return self._results.pop(0)


def _success(name: str) -> TranscribeSingleFileSuccess:
    return TranscribeSingleFileSuccess(
        name, Path(f"C:/evidence/{name}.txt"), (), AttemptState.COMPLETED
    )


def _failure(category: AttemptFailure = AttemptFailure.NETWORK) -> TranscribeSingleFileFailure:
    state = AttemptState.CANCELLED if category is AttemptFailure.CANCELLED else AttemptState.FAILED
    return TranscribeSingleFileFailure("evidence", category, True, "safe", "SAFE", state)


def _window(use_case: _UseCase) -> MainWindow:
    events = QtBatchEvents()
    processor = BatchProcessor(
        use_case,
        BatchSettings(OUTPUT, OUTPUT / "cache", OutputFormat.TXT),
        events,
        "ux-evidence",
    )
    window = MainWindow(processor, events, OUTPUT / "cache", QWidget, _Notice())
    window.set_output_directory(OUTPUT)
    window.resize(980, 700)
    window.show()
    QApplication.processEvents()
    return window


def _wait(predicate: Callable[[], bool], timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise RuntimeError("UX_EVIDENCE_TIMEOUT")
        QApplication.processEvents()
        time.sleep(0.01)


def _save(window: MainWindow, name: str) -> None:
    QApplication.processEvents()
    if not window.grab().save(str(OUTPUT / name), "PNG"):
        raise RuntimeError("UX_EVIDENCE_SAVE_FAILED")


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    _ = app
    OUTPUT.mkdir(parents=True, exist_ok=True)

    empty = _window(_UseCase([]))
    _save(empty, "01-empty.png")
    empty.close()

    release = Event()
    running_case = _UseCase([_success("one"), _success("two")], release)
    running = _window(running_case)
    running.set_sources([Path("reuniao-longa.mp4"), Path("entrevista.wav")])
    running.start_button.click()
    _wait(running_case.entered.is_set)
    _save(running, "02-running.png")
    release.set()
    _wait(lambda: running._thread is None)
    running.close()

    partial = _window(_UseCase([_success("one"), _failure(), _success("three")]))
    partial.set_sources([Path("aula.mp4"), Path("falha.wav"), Path("podcast.mp3")])
    partial.start_button.click()
    _wait(lambda: partial._thread is None)
    _save(partial, "03-partial-failure.png")
    partial.close()

    resume = _window(_UseCase([]))
    resume.set_sources([Path("gravacao-interrompida.mp4")])
    resume.show_resume_banner()
    _save(resume, "04-resume.png")
    resume.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
