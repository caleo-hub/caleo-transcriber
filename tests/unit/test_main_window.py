from collections.abc import Callable
from pathlib import Path
from threading import Event

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget
from pytestqt.qtbot import QtBot

from caleo_transcriber.application import (
    AttemptEvents,
    AttemptFailure,
    TranscribeSingleFileCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileResult,
    TranscribeSingleFileSuccess,
    TranscribeSingleFileUseCase,
)
from caleo_transcriber.domain import AttemptState
from caleo_transcriber.presentation import MainWindow, QSettingsCloudNoticePolicy, QtAttemptEvents


class SeenNotice:
    def __init__(self, seen: bool = True) -> None:
        self.seen = seen
        self.mark_calls = 0

    def should_show(self) -> bool:
        return not self.seen

    def mark_shown(self) -> None:
        self.seen = True
        self.mark_calls += 1


class StubUseCase:
    def __init__(
        self,
        results: TranscribeSingleFileResult | Exception | list[TranscribeSingleFileResult],
        before_result: Callable[[], None] | None = None,
    ) -> None:
        self._results = results if isinstance(results, list) else [results]
        self._before_result = before_result
        self.calls: list[TranscribeSingleFileCommand] = []

    def execute(
        self,
        command: TranscribeSingleFileCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        if self._before_result is not None:
            self._before_result()
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class CancellableUseCase:
    def __init__(self) -> None:
        self.entered = Event()
        self.release = Event()

    def execute(
        self,
        command: TranscribeSingleFileCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.entered.set()
        while not self.release.wait(0.01):
            if should_cancel is not None and should_cancel():
                return TranscribeSingleFileFailure(
                    command.attempt_id,
                    AttemptFailure.CANCELLED,
                    False,
                    "safe.message",
                    "CANCELLED",
                    AttemptState.CANCELLED,
                )
        return _success()


def _success() -> TranscribeSingleFileSuccess:
    return TranscribeSingleFileSuccess(
        "attempt",
        Path("C:/synthetic-output/aula.txt"),
        (),
    )


def _failure() -> TranscribeSingleFileFailure:
    return TranscribeSingleFileFailure(
        "attempt",
        AttemptFailure.NETWORK,
        True,
        "safe.message",
        "NETWORK",
        AttemptState.FAILED,
    )


def _window(
    qtbot: QtBot,
    use_case: TranscribeSingleFileUseCase,
    notice: SeenNotice | None = None,
) -> MainWindow:
    events = QtAttemptEvents()
    window = MainWindow(
        use_case,
        events,
        Path("C:/synthetic-cache"),
        QWidget,
        notice or SeenNotice(),
    )
    qtbot.addWidget(window)
    window.show()
    return window


def _configure(window: MainWindow) -> None:
    window.set_source(Path("C:/synthetic-input/aula.mp4"))
    window.set_output_directory(Path("C:/synthetic-output"))


def _click(qtbot: QtBot, button: QPushButton) -> None:
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)  # type: ignore[no-untyped-call]


def test_ui_has_permanent_cloud_notice_labels_focus_and_no_history(qtbot: QtBot) -> None:
    use_case = StubUseCase(_success())
    window = _window(qtbot, use_case)

    labels = [label.text() for label in window.findChildren(QLabel)]
    assert "OpenAI (cloud)" in labels
    assert "Envia somente o áudio selecionado e pode gerar custo." in labels
    assert window.source_field.accessibleName() == "Arquivo selecionado"
    assert window.output_field.accessibleName() == "Pasta de saída selecionada"
    assert window.status_label.text() == "Selecione o arquivo e a pasta de saída."
    assert window.start_button.isEnabled() is False
    assert window.progress.isVisible() is False
    assert isinstance(window._events, AttemptEvents)


def test_worker_keeps_ui_responsive_and_completes_without_fake_percentage(
    qtbot: QtBot,
) -> None:
    entered = Event()
    release = Event()

    def wait_for_test() -> None:
        entered.set()
        assert release.wait(timeout=5)

    use_case = StubUseCase(_success(), wait_for_test)
    window = _window(qtbot, use_case)
    _configure(window)

    _click(qtbot, window.start_button)
    assert entered.wait(timeout=5)
    qtbot.waitUntil(window.cancel_button.isEnabled, timeout=1_000)
    assert window.isEnabled()
    assert window.progress.minimum() == 0
    assert window.progress.maximum() == 0

    release.set()
    qtbot.waitUntil(lambda: window.status_label.text() == "Transcrição concluída")
    qtbot.waitUntil(window.open_output_button.isEnabled)
    assert window.detail_label.text() == "Arquivo criado: aula.txt"


def test_cancel_and_retry_are_available_with_safe_text(qtbot: QtBot) -> None:
    cancellable = CancellableUseCase()
    window = _window(qtbot, cancellable)
    _configure(window)

    _click(qtbot, window.start_button)
    assert cancellable.entered.wait(timeout=5)
    _click(qtbot, window.cancel_button)

    qtbot.waitUntil(lambda: window.status_label.text() == "Transcrição cancelada")
    qtbot.waitUntil(window.retry_button.isEnabled)
    assert "temporários" in window.detail_label.text()


def test_failure_can_be_retried_and_worker_exception_does_not_close_window(
    qtbot: QtBot,
) -> None:
    results: list[TranscribeSingleFileResult] = [_failure(), _success()]
    use_case = StubUseCase(results)
    window = _window(qtbot, use_case)
    _configure(window)

    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: window.status_label.text() == "Não foi possível concluir")
    qtbot.waitUntil(window.retry_button.isEnabled)
    _click(qtbot, window.retry_button)
    qtbot.waitUntil(lambda: window.status_label.text() == "Transcrição concluída")
    assert len(use_case.calls) == 2
    assert window.isVisible()

    error_window = _window(qtbot, StubUseCase(RuntimeError("sensitive detail")))
    _configure(error_window)
    _click(qtbot, error_window.start_button)
    qtbot.waitUntil(lambda: error_window.status_label.text() == "Não foi possível concluir")
    assert "sensitive" not in error_window.detail_label.text()
    assert error_window.isVisible()


def test_first_cloud_notice_is_shown_once(qtbot: QtBot, monkeypatch: pytest.MonkeyPatch) -> None:
    notice = SeenNotice(False)
    calls = 0

    def information(*args: object, **kwargs: object) -> QMessageBox.StandardButton:
        nonlocal calls
        calls += 1
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "information", information)
    use_case = StubUseCase([_success(), _success()])
    window = _window(qtbot, use_case, notice)
    _configure(window)

    _click(qtbot, window.start_button)
    qtbot.waitUntil(window.open_output_button.isEnabled)
    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: len(use_case.calls) == 2)
    qtbot.waitUntil(window.open_output_button.isEnabled)

    assert calls == 1
    assert notice.mark_calls == 1


def test_qsettings_notice_persists_only_non_secret_boolean(tmp_path: Path) -> None:
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    policy = QSettingsCloudNoticePolicy(settings)

    assert policy.should_show() is True
    policy.mark_shown()

    assert policy.should_show() is False
    text = (tmp_path / "settings.ini").read_text(encoding="utf-8")
    assert "openai-cloud-notice-shown=true" in text
    assert "key" not in text.lower()
