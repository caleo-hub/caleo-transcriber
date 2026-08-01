from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QAbstractItemView, QLabel, QMessageBox, QWidget
from pytestqt.qtbot import QtBot

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
        results: list[TranscribeSingleFileResult],
        entered: Event | None = None,
        release: Event | None = None,
    ) -> None:
        self.results = results
        self.calls: list[TranscribeLongMediaCommand] = []
        self.entered = entered
        self.release = release

    def execute(
        self,
        command: TranscribeLongMediaCommand,
        should_cancel: Callable[[], bool] | None = None,
    ) -> TranscribeSingleFileResult:
        self.calls.append(command)
        if self.entered is not None:
            self.entered.set()
        if self.release is not None:
            while not self.release.wait(0.005):
                if should_cancel is not None and should_cancel():
                    return _failure(AttemptFailure.CANCELLED)
        return self.results.pop(0)


def _success() -> TranscribeSingleFileSuccess:
    return TranscribeSingleFileSuccess(
        "attempt", Path("C:/synthetic-output/aula.txt"), (), AttemptState.COMPLETED
    )


def _failure(category: AttemptFailure = AttemptFailure.NETWORK) -> TranscribeSingleFileFailure:
    state = AttemptState.CANCELLED if category is AttemptFailure.CANCELLED else AttemptState.FAILED
    return TranscribeSingleFileFailure("attempt", category, True, "safe", "SAFE", state)


def _window(
    qtbot: QtBot,
    use_case: StubUseCase,
    notice: SeenNotice | None = None,
) -> MainWindow:
    events = QtBatchEvents()
    processor = BatchProcessor(
        use_case,
        BatchSettings(Path("C:/out"), Path("C:/cache"), OutputFormat.TXT),
        events,
        "batch-test",
    )
    window = MainWindow(
        processor,
        events,
        Path("C:/cache"),
        QWidget,
        notice or SeenNotice(),
    )
    qtbot.addWidget(window)
    window.show()
    return window


def _click(qtbot: QtBot, widget: QWidget) -> None:
    qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)  # type: ignore[no-untyped-call]


def _cell_text(window: MainWindow, row: int, column: int) -> str:
    item = window.table.item(row, column)
    assert item is not None
    return item.text()


def _select_rows(window: MainWindow, *rows: int) -> None:
    selection = window.table.selectionModel()
    selection.clearSelection()
    flags = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
    for row in rows:
        selection.select(window.table.model().index(row, 0), flags)


def test_empty_ui_has_cloud_notice_accessible_queue_and_no_history(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([]))
    labels = [label.text() for label in window.findChildren(QLabel)]

    assert "OpenAI (cloud)" in labels
    assert "Envia somente o áudio de cada item e pode gerar custo." in labels
    assert window.table.accessibleName() == "Fila de arquivos para transcrição"
    assert not window.windowIcon().isNull()
    assert window.table.rowCount() == 0
    assert "nenhum histórico" in window.summary_label.text()
    assert not window.start_button.isEnabled()


def test_multiple_sources_deduplicate_and_format_is_common(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([]))
    window.set_sources([Path("one.mp4"), Path("two.wav"), Path("one.mp4")])
    window.set_output_directory(Path("C:/out"))
    window.format_combo.setCurrentIndex(1)

    assert window.table.rowCount() == 2
    assert [_cell_text(window, row, 0) for row in range(2)] == ["one.mp4", "two.wav"]
    assert [_cell_text(window, row, 2) for row in range(2)] == ["SRT", "SRT"]
    assert "duplicado" in window.detail_label.text()
    assert window.start_button.isEnabled()


def test_selection_reorders_and_removes_queue_items(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([]))
    window.set_sources([Path("one.mp4"), Path("two.mp4"), Path("three.mp4")])
    window.set_output_directory(Path("C:/out"))

    assert window.table.selectionMode() == QAbstractItemView.SelectionMode.ExtendedSelection
    _select_rows(window, 1)
    assert window.move_up_button.isEnabled()
    _click(qtbot, window.move_up_button)
    assert [_cell_text(window, row, 0) for row in range(3)] == [
        "two.mp4",
        "one.mp4",
        "three.mp4",
    ]

    _select_rows(window, 0, 2)
    assert window.remove_button.isEnabled()
    _click(qtbot, window.remove_button)
    assert window.table.rowCount() == 1
    assert _cell_text(window, 0, 0) == "one.mp4"
    assert "somente da fila" in window.detail_label.text()


def test_pause_after_current_leaves_next_item_ready(qtbot: QtBot) -> None:
    entered = Event()
    release = Event()
    use_case = StubUseCase([_success(), _success()], entered, release)
    window = _window(qtbot, use_case)
    window.set_sources([Path("one.mp4"), Path("two.mp4")])
    window.set_output_directory(Path("C:/out"))

    _click(qtbot, window.start_button)
    assert entered.wait(timeout=2)
    qtbot.waitUntil(window.pause_button.isEnabled)
    _click(qtbot, window.pause_button)
    release.set()
    qtbot.waitUntil(lambda: window._thread is None)

    assert len(use_case.calls) == 1
    assert _cell_text(window, 0, 3) == "Concluído"
    assert _cell_text(window, 1, 3) == "Na fila"
    assert window.start_button.isEnabled()


def test_retry_selected_requeues_only_selected_failure(qtbot: QtBot) -> None:
    use_case = StubUseCase([_failure(), _failure(), _success()])
    window = _window(qtbot, use_case)
    window.set_sources([Path("one.mp4"), Path("two.mp4")])
    window.set_output_directory(Path("C:/out"))
    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: window._thread is None)

    _select_rows(window, 1)
    assert window.retry_selected_button.isEnabled()
    _click(qtbot, window.retry_selected_button)
    qtbot.waitUntil(lambda: window._thread is None and len(use_case.calls) == 3)

    assert [call.source.name for call in use_case.calls] == ["one.mp4", "two.mp4", "two.mp4"]
    assert _cell_text(window, 0, 3) == "Falhou — conexão"
    assert _cell_text(window, 1, 3) == "Concluído"


def test_clear_completed_preserves_files_message_and_cancel_actions(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([_success()]))
    window.set_sources([Path("one.mp4")])
    window.set_output_directory(Path("C:/out"))
    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: window._thread is None)

    assert window.clear_completed_action.isEnabled()
    window.clear_completed_action.trigger()

    assert window.table.rowCount() == 0
    assert "arquivos foram preservados" in window.detail_label.text()
    assert window.cancel_button.text() == "&Cancelar atual"
    assert window.cancel_all_action.text() == "Cancelar fila"


def test_worker_keeps_ui_responsive_and_locks_configuration(qtbot: QtBot) -> None:
    entered = Event()
    release = Event()
    use_case = StubUseCase([_success()], entered, release)
    window = _window(qtbot, use_case)
    window.set_sources([Path("one.mp4")])
    window.set_output_directory(Path("C:/out"))

    _click(qtbot, window.start_button)
    assert entered.wait(timeout=2)
    qtbot.waitUntil(window.cancel_button.isEnabled)
    assert window.isEnabled()
    assert not window.add_button.isEnabled()
    assert window.progress.minimum() == 0 and window.progress.maximum() == 0

    release.set()
    qtbot.waitUntil(lambda: "1 de 1" in window.summary_label.text())
    qtbot.waitUntil(window.add_button.isEnabled)
    assert "1 concluídos" in window.summary_label.text()


def test_failure_is_inline_and_retry_only_failure(qtbot: QtBot) -> None:
    use_case = StubUseCase([_failure(), _success(), _success()])
    window = _window(qtbot, use_case)
    window.set_sources([Path("one.mp4"), Path("two.mp4")])
    window.set_output_directory(Path("C:/out"))

    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: "1 falharam" in window.summary_label.text())
    qtbot.waitUntil(window.retry_button.isEnabled)
    assert _cell_text(window, 0, 3) == "Falhou — conexão"
    assert "Verifique a internet" in window.detail_label.text()
    assert "SAFE" in window.detail_label.text()
    assert "one.mp4" not in window.detail_label.text()
    assert window.isVisible()
    _click(qtbot, window.retry_button)
    qtbot.waitUntil(lambda: len(use_case.calls) == 3)
    qtbot.waitUntil(lambda: "2 concluídos" in window.summary_label.text())
    qtbot.waitUntil(lambda: window._thread is None)
    assert [call.source.name for call in use_case.calls] == ["one.mp4", "two.mp4", "one.mp4"]


def test_theme_explicitly_styles_dark_mode_surfaces(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([]))
    style = window.styleSheet()

    assert "QMainWindow, QDialog { background: #F4F7FB; }" in style
    assert "QPushButton, QComboBox, QLineEdit" in style
    assert "QHeaderView::section" in style
    assert "background: #E8EEF6; color: #102A43" in style
    assert "QMenu {" in style
    assert "QMenu::item:selected { background: #D6E9FF; color: #102A43; }" in style
    assert "QMenu::item:disabled { background: transparent; color: #6B7C8F; }" in style
    assert "QMenu::separator" in style
    assert window.clear_menu.objectName() == "queueMenu"
    assert window.more_button.menu() is window.clear_menu

    dialog = window._create_settings_dialog()
    qtbot.addWidget(dialog)
    assert dialog.objectName() == "settingsDialog"
    assert dialog.minimumWidth() >= 520
    assert dialog.styleSheet() == style


def test_credential_failure_explains_recovery_without_exposing_path(qtbot: QtBot) -> None:
    use_case = StubUseCase([_failure(AttemptFailure.CREDENTIAL)])
    window = _window(qtbot, use_case)
    window.set_sources([Path("private-demo.mp4")])
    window.set_output_directory(Path("C:/out"))

    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: window._thread is None)

    assert _cell_text(window, 0, 3) == "Falhou — chave OpenAI"
    assert "Configurar chave" in window.detail_label.text()
    assert "SAFE" in window.detail_label.text()
    assert "private-demo.mp4" not in window.detail_label.text()


def test_first_cloud_notice_is_shown_once(qtbot: QtBot, monkeypatch: pytest.MonkeyPatch) -> None:
    notice = SeenNotice(False)
    calls = 0

    def information(*args: object, **kwargs: object) -> QMessageBox.StandardButton:
        nonlocal calls
        calls += 1
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "information", information)
    window = _window(qtbot, StubUseCase([_success()]), notice)
    window.set_sources([Path("one.mp4")])
    window.set_output_directory(Path("C:/out"))

    _click(qtbot, window.start_button)
    qtbot.waitUntil(lambda: "1 concluídos" in window.summary_label.text())
    qtbot.waitUntil(lambda: window._thread is None)

    assert calls == 1
    assert notice.mark_calls == 1


def test_approved_resume_banner_text_is_available(qtbot: QtBot) -> None:
    window = _window(qtbot, StubUseCase([]))

    window.show_resume_banner()

    assert window.banner.isVisible()
    assert window.banner_label.text() == "Continuar processamento interrompido?"
    assert window.banner_action.text() == "Continuar"
    assert window.banner_dismiss.text() == "Descartar e começar de novo"
