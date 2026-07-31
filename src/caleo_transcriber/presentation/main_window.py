"""Janela desktop acessível para fila efêmera de transcrições."""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QCloseEvent, QDesktopServices, QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from caleo_transcriber import __version__
from caleo_transcriber.application import (
    AttemptEvent,
    AttemptFailure,
    BatchProcessor,
    BatchQueueEvent,
    BatchSettings,
    OutputFormat,
    TranscribeSingleFileFailure,
)
from caleo_transcriber.domain import AttemptState, BatchItemState
from caleo_transcriber.presentation.notices import CloudNoticePolicy
from caleo_transcriber.presentation.worker import BatchWorker

_SUPPORTED = {".mp4", ".mp3", ".wav"}
_STATE_TEXT = {
    BatchItemState.QUEUED: "Na fila",
    BatchItemState.PREPARING: "Preparando áudio",
    BatchItemState.TRANSCRIBING: "Transcrevendo",
    BatchItemState.SAVING: "Salvando",
    BatchItemState.COMPLETED: "Concluído",
    BatchItemState.FAILED: "Falhou",
    BatchItemState.CANCELLING: "Cancelando",
    BatchItemState.CANCELLED: "Cancelado",
}

_FAILURE_STATUS = {
    AttemptFailure.INVALID_INPUT: "Falhou — mídia inválida",
    AttemptFailure.UNSUPPORTED_MEDIA: "Falhou — formato não suportado",
    AttemptFailure.CREDENTIAL: "Falhou — chave OpenAI",
    AttemptFailure.NETWORK: "Falhou — conexão",
    AttemptFailure.RATE_LIMIT: "Falhou — limite OpenAI",
    AttemptFailure.PROVIDER: "Falhou — OpenAI",
    AttemptFailure.CANCELLED: "Cancelado",
    AttemptFailure.OUTPUT: "Falhou — pasta de saída",
    AttemptFailure.AMBIGUOUS: "Falhou — envio incerto",
}

_FAILURE_GUIDANCE = {
    AttemptFailure.INVALID_INPUT: (
        "Não foi possível preparar a mídia. Confirme se o arquivo contém uma faixa de áudio "
        "legível e tente novamente."
    ),
    AttemptFailure.UNSUPPORTED_MEDIA: "Use um arquivo MP4, MP3 ou WAV válido.",
    AttemptFailure.CREDENTIAL: (
        "A chave da OpenAI está ausente ou foi recusada. Abra Configurar chave, salve uma chave "
        "válida e repita o item."
    ),
    AttemptFailure.NETWORK: (
        "Não foi possível conectar à OpenAI. Verifique a internet e repita o item."
    ),
    AttemptFailure.RATE_LIMIT: (
        "A OpenAI recusou temporariamente a solicitação por limite ou cota. Aguarde e repita."
    ),
    AttemptFailure.PROVIDER: (
        "A OpenAI não concluiu a transcrição. Repita o item; se continuar, informe o código abaixo."
    ),
    AttemptFailure.CANCELLED: "O item foi cancelado sem publicar uma saída parcial.",
    AttemptFailure.OUTPUT: (
        "Não foi possível salvar a transcrição. Escolha outra pasta de saída e repita o item."
    ),
    AttemptFailure.AMBIGUOUS: (
        "O envio pode ter sido processado pela OpenAI. Confirme antes de reenviar para evitar "
        "cobrança duplicada."
    ),
}


class QtBatchEvents(QObject):
    event_published = Signal(object)

    def publish(self, event: BatchQueueEvent) -> None:
        self.event_published.emit(event)


class QtAttemptEvents(QObject):
    event_published = Signal(object)

    def publish(self, event: AttemptEvent) -> None:
        self.event_published.emit(event)


class MainWindow(QMainWindow):
    def __init__(
        self,
        processor: BatchProcessor,
        events: QtBatchEvents,
        workspace: Path,
        settings_widget_factory: Callable[[], QWidget],
        notice_policy: CloudNoticePolicy,
        attempt_events: QtAttemptEvents | None = None,
    ) -> None:
        super().__init__()
        self._processor = processor
        self._events = events
        self._workspace = workspace
        self._settings_widget_factory = settings_widget_factory
        self._notice_policy = notice_policy
        self._attempt_events = attempt_events
        self._output_directory: Path | None = None
        self._thread: QThread | None = None
        self._worker: BatchWorker | None = None
        self._rows: dict[str, int] = {}
        self._close_when_finished = False

        self.setWindowTitle(f"Caleo Transcriber {__version__}")
        icon_path = _application_icon_path()
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setMinimumSize(880, 620)
        self.resize(980, 700)
        self.setAcceptDrops(True)
        self._build_ui()
        self._apply_style()
        self._events.event_published.connect(self._on_batch_event)
        if self._attempt_events is not None:
            self._attempt_events.event_published.connect(self._on_attempt_event)
        self._refresh()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel(f"Caleo Transcriber  {__version__}")
        title.setObjectName("title")
        subtitle = QLabel("Transcreva vários áudios e vídeos em uma fila simples.")
        subtitle.setObjectName("muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.settings_button = QPushButton("&Configurar chave")
        self.settings_button.setAccessibleName("Configurar chave da OpenAI")
        self.settings_button.clicked.connect(self._open_settings)
        header.addWidget(self.settings_button)
        root.addLayout(header)

        cloud = QFrame()
        cloud.setObjectName("cloudCard")
        cloud_layout = QHBoxLayout(cloud)
        cloud_title = QLabel("OpenAI (cloud)")
        cloud_title.setObjectName("cloudTitle")
        cloud_text = QLabel("Envia somente o áudio de cada item e pode gerar custo.")
        cloud_text.setAccessibleName("Aviso permanente do modo OpenAI cloud")
        cloud_layout.addWidget(cloud_title)
        cloud_layout.addWidget(cloud_text, 1)
        root.addWidget(cloud)

        self.banner = QFrame()
        self.banner.setObjectName("banner")
        banner_layout = QHBoxLayout(self.banner)
        self.banner_label = QLabel()
        self.banner_label.setWordWrap(True)
        self.banner_label.setAccessibleName("Aviso de retomada")
        self.banner_action = QPushButton("Continuar")
        self.banner_dismiss = QPushButton("Descartar")
        self.banner_dismiss.clicked.connect(self.banner.hide)
        banner_layout.addWidget(self.banner_label, 1)
        banner_layout.addWidget(self.banner_action)
        banner_layout.addWidget(self.banner_dismiss)
        self.banner.hide()
        root.addWidget(self.banner)

        toolbar = QHBoxLayout()
        self.add_button = QPushButton("&Adicionar arquivos")
        self.add_button.setAccessibleName("Adicionar vários arquivos à fila")
        self.add_button.clicked.connect(self._choose_sources)
        self.output_button = QPushButton("Escolher &pasta de saída")
        self.output_button.clicked.connect(self._choose_output)
        self.output_label = QLabel("Pasta de saída não escolhida")
        self.output_label.setObjectName("muted")
        self.output_label.setAccessibleName("Pasta de saída selecionada")
        self.format_combo = QComboBox()
        self.format_combo.addItem("TXT", OutputFormat.TXT)
        self.format_combo.addItem("SRT", OutputFormat.SRT)
        self.format_combo.setAccessibleName("Formato de saída")
        self.format_combo.currentIndexChanged.connect(self._refresh_format_column)
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.output_button)
        toolbar.addWidget(self.output_label, 1)
        toolbar.addWidget(QLabel("Formato:"))
        toolbar.addWidget(self.format_combo)
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Arquivo", "Duração", "Formato", "Estado", "Ação"])
        self.table.setAccessibleName("Fila de arquivos para transcrição")
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, 5):
            header_view.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table, 1)

        status = QFrame()
        status.setObjectName("card")
        status_layout = QVBoxLayout(status)
        self.summary_label = QLabel("Fila vazia — nenhum histórico é mantido.")
        self.summary_label.setAccessibleName("Resumo da fila")
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setAccessibleName("Atividade do item atual")
        self.progress.hide()
        self.detail_label = QLabel(
            "Adicione MP4, MP3 ou WAV; arquivos longos são divididos automaticamente."
        )
        self.detail_label.setObjectName("muted")
        self.detail_label.setWordWrap(True)
        status_layout.addWidget(self.summary_label)
        status_layout.addWidget(self.progress)
        status_layout.addWidget(self.detail_label)
        root.addWidget(status)

        actions = QHBoxLayout()
        self.start_button = QPushButton("&Iniciar fila")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self._start)
        self.cancel_button = QPushButton("&Cancelar fila")
        self.cancel_button.clicked.connect(self._cancel_all)
        self.retry_button = QPushButton("&Repetir falhas")
        self.retry_button.clicked.connect(self._retry_failed)
        actions.addWidget(self.start_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.retry_button)
        actions.addStretch()
        root.addLayout(actions)
        self.setCentralWidget(central)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget { font-family: "Segoe UI"; font-size: 13px; color: #152238; }
            QMainWindow, QDialog { background: #F4F7FB; }
            QLabel#title { font-size: 25px; font-weight: 700; color: #102A43; }
            QLabel#muted { color: #62748A; }
            QFrame#card, QTableWidget {
                background: white; border: 1px solid #D9E2EC; border-radius: 8px;
            }
            QFrame#cloudCard { background: #E8F3FF; border: 1px solid #9BC7F5; border-radius: 8px; }
            QFrame#banner { background: #FFF4D6; border: 1px solid #E0A800; border-radius: 8px; }
            QLabel#cloudTitle { font-weight: 700; color: #0B5CAD; }
            QPushButton, QComboBox, QLineEdit {
                background: white; color: #152238; border: 1px solid #829AB1;
                border-radius: 6px; padding: 8px 12px;
            }
            QPushButton:hover, QComboBox:hover { background: #EDF6FF; border-color: #1677C8; }
            QPushButton:focus, QComboBox:focus, QLineEdit:focus, QTableWidget:focus {
                border: 2px solid #1677C8;
            }
            QPushButton:disabled, QComboBox:disabled, QLineEdit:disabled {
                color: #6B7C8F; background: #E8EDF3; border-color: #B8C4D1;
            }
            QPushButton#primaryButton {
                background: #1261A0; color: white;
                border-color: #1261A0; font-weight: 700;
            }
            QPushButton#primaryButton:hover { background: #0B528D; }
            QTableWidget {
                color: #152238; gridline-color: #D9E2EC;
                alternate-background-color: #F4F7FB;
                selection-background-color: #D6E9FF; selection-color: #102A43;
            }
            QHeaderView::section {
                background: #E8EEF6; color: #102A43; font-weight: 700;
                border: none; border-right: 1px solid #C8D4E1;
                border-bottom: 1px solid #B8C7D9; padding: 7px 8px;
            }
            QTableCornerButton::section {
                background: #E8EEF6; border: none; border-bottom: 1px solid #B8C7D9;
            }
            QComboBox QAbstractItemView {
                background: white; color: #152238; border: 1px solid #829AB1;
                selection-background-color: #D6E9FF; selection-color: #102A43;
            }
            QToolTip {
                background: #102A43; color: white; border: 1px solid #486581; padding: 4px;
            }
            QProgressBar { min-height: 8px; max-height: 8px; border: none; background: #D9E2EC; }
            QProgressBar::chunk { background: #1677C8; }
            """
        )

    def set_sources(self, sources: Iterable[Path]) -> None:
        supported = [source for source in sources if source.suffix.lower() in _SUPPORTED]
        result = self._processor.add_sources(supported)
        self._rebuild_table()
        if result.duplicate_count:
            self.detail_label.setText(
                f"{result.duplicate_count} arquivo(s) duplicado(s) não foram adicionados."
            )
        elif len(supported) == 0:
            self.detail_label.setText("Nenhum arquivo MP4, MP3 ou WAV válido foi adicionado.")
        self._refresh()

    def set_output_directory(self, directory: Path) -> None:
        self._output_directory = directory
        self.output_label.setText(str(directory))
        self.output_label.setToolTip(str(directory))
        self._refresh()

    @Slot()
    def _choose_sources(self) -> None:
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Adicionar áudios ou vídeos", "", "Mídia suportada (*.mp4 *.mp3 *.wav)"
        )
        if filenames:
            self.set_sources(Path(name) for name in filenames)

    @Slot()
    def _choose_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Escolher pasta de saída")
        if directory:
            self.set_output_directory(Path(directory))

    @Slot()
    def _start(self) -> None:
        if self._thread is not None or self._output_directory is None:
            return
        if self._notice_policy.should_show():
            QMessageBox.information(
                self,
                "Antes de usar a OpenAI",
                "Este modo envia somente áudio preparado para a OpenAI e pode gerar custo.",
            )
            self._notice_policy.mark_shown()
        self._processor.configure(
            BatchSettings(
                self._output_directory,
                self._workspace,
                self._format(),
            )
        )
        thread = QThread(self)
        worker = BatchWorker(self._processor)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.summary_ready.connect(lambda _: self._refresh())
        worker.safe_error.connect(self._on_worker_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        self._thread = thread
        self._worker = worker
        self.progress.setRange(0, 0)
        self.progress.show()
        self.detail_label.setText("Um item por vez; a etapa atual não é convertida em percentual.")
        self._refresh()
        thread.start()

    @Slot()
    def _cancel_all(self) -> None:
        self._processor.cancel_all()
        self.detail_label.setText("Cancelamento solicitado; itens concluídos serão preservados.")
        self._refresh()

    @Slot()
    def _retry_failed(self) -> None:
        if self._processor.retry_failed():
            self._rebuild_table()
            self._start()

    @Slot(object)
    def _on_batch_event(self, value: object) -> None:
        if not isinstance(value, BatchQueueEvent):
            return
        if value.item_id not in self._rows:
            self._rebuild_table()
        row = self._rows.get(value.item_id)
        result = self._processor.result_for(value.item_id)
        if row is not None:
            status_text = _STATE_TEXT[value.state]
            if value.state is BatchItemState.FAILED and isinstance(
                result, TranscribeSingleFileFailure
            ):
                status_text = _FAILURE_STATUS[result.category]
                guidance = _failure_guidance(result)
                self.detail_label.setText(guidance)
            status_item = QTableWidgetItem(status_text)
            if value.state is BatchItemState.FAILED and isinstance(
                result, TranscribeSingleFileFailure
            ):
                status_item.setToolTip(_failure_guidance(result))
            self.table.setItem(row, 3, status_item)
            self._set_action(row, value.item_id, value.state)
        if value.state is BatchItemState.FAILED:
            if isinstance(result, TranscribeSingleFileFailure) and (
                result.category is AttemptFailure.AMBIGUOUS
            ):
                self._show_ambiguous_banner(value.item_id)
        self._refresh_summary()

    @Slot(object)
    def _on_attempt_event(self, value: object) -> None:
        if not isinstance(value, AttemptEvent):
            return
        row = self._rows.get(value.attempt_id)
        if row is None:
            return
        state_text = {
            AttemptState.READY: "Pronto",
            AttemptState.PREPARING: "Preparando áudio",
            AttemptState.TRANSCRIBING: "Transcrevendo",
            AttemptState.SAVING: "Salvando",
            AttemptState.COMPLETED: "Concluído",
            AttemptState.FAILED: "Falhou",
            AttemptState.CANCELLING: "Cancelando",
            AttemptState.CANCELLED: "Cancelado",
        }[value.state]
        if value.total_chunks is not None and value.state is AttemptState.TRANSCRIBING:
            state_text += f" — {value.completed_chunks}/{value.total_chunks} partes"
        self.table.setItem(row, 3, QTableWidgetItem(state_text))

    def _show_ambiguous_banner(self, item_id: str) -> None:
        self.banner_label.setText("Esta parte pode já ter sido cobrada. Reenviar?")
        self.banner_action.setText("Reenviar parte")
        try:
            self.banner_action.clicked.disconnect()
        except RuntimeError:
            pass
        self.banner_action.clicked.connect(lambda: self._confirm_ambiguous(item_id))
        self.banner_dismiss.setText("Não reenviar")
        self.banner.show()

    def show_resume_banner(self) -> None:
        """Exibe o aviso aprovado quando o bootstrap detectar checkpoint compatível."""

        self.banner_label.setText("Continuar processamento interrompido?")
        self.banner_action.setText("Continuar")
        self.banner_dismiss.setText("Descartar e começar de novo")
        self.banner.show()

    def _confirm_ambiguous(self, item_id: str) -> None:
        if self._processor.retry_ambiguous(item_id):
            self.banner.hide()
            self._rebuild_table()
            self._start()

    def _rebuild_table(self) -> None:
        items = self._processor.items
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 4)
            if widget is not None:
                self.table.removeCellWidget(row, 4)
                widget.setParent(None)
                widget.deleteLater()
        self.table.setRowCount(0)
        self.table.setRowCount(len(items))
        self._rows.clear()
        for row, item in enumerate(items):
            self._rows[item.item_id] = row
            source = Path(item.source_identity)
            file_item = QTableWidgetItem(source.name)
            file_item.setToolTip(item.source_identity)
            self.table.setItem(row, 0, file_item)
            self.table.setItem(row, 1, QTableWidgetItem("—"))
            self.table.setItem(row, 2, QTableWidgetItem(self._format().value.upper()))
            status_text = _STATE_TEXT[item.state]
            result = self._processor.result_for(item.item_id)
            status_item = QTableWidgetItem(status_text)
            if item.state is BatchItemState.FAILED and isinstance(
                result, TranscribeSingleFileFailure
            ):
                status_item.setText(_FAILURE_STATUS[result.category])
                status_item.setToolTip(_failure_guidance(result))
            self.table.setItem(row, 3, status_item)
            self._set_action(row, item.item_id, item.state)

    def _set_action(self, row: int, item_id: str, state: BatchItemState) -> None:
        existing = self.table.cellWidget(row, 4)
        button = existing if isinstance(existing, QPushButton) else QPushButton()
        if existing is None:
            button.clicked.connect(
                lambda _checked=False, current=button: self._run_row_action(current)
            )
        button.setEnabled(True)
        button.setProperty("item_id", item_id)
        if state in {BatchItemState.QUEUED, BatchItemState.PREPARING, BatchItemState.TRANSCRIBING}:
            button.setText("Cancelar")
            button.setAccessibleName(f"Cancelar item {row + 1}")
            button.setProperty("action", "cancel")
        elif state is BatchItemState.COMPLETED:
            button.setText("Abrir pasta")
            button.setProperty("action", "open")
        else:
            button.setText("—")
            button.setEnabled(False)
            button.setProperty("action", "none")
        if existing is None:
            self.table.setCellWidget(row, 4, button)

    def _run_row_action(self, button: QPushButton) -> None:
        action = button.property("action")
        if action == "cancel":
            item_id = button.property("item_id")
            if isinstance(item_id, str):
                self._cancel_item(item_id)
        elif action == "open":
            self._open_output()

    def _cancel_item(self, item_id: str) -> None:
        self._processor.cancel_item(item_id)
        self._refresh()

    def _refresh_format_column(self) -> None:
        for row in range(self.table.rowCount()):
            self.table.setItem(row, 2, QTableWidgetItem(self._format().value.upper()))

    def _format(self) -> OutputFormat:
        value = self.format_combo.currentData()
        try:
            return OutputFormat(str(value))
        except ValueError:
            return OutputFormat.TXT

    def _refresh(self) -> None:
        active = self._thread is not None
        summary = self._processor.summary()
        queued = any(item.state is BatchItemState.QUEUED for item in self._processor.items)
        self.start_button.setEnabled(not active and queued and self._output_directory is not None)
        self.cancel_button.setEnabled(active)
        self.retry_button.setEnabled(not active and summary.failed > 0)
        for widget in (
            self.add_button,
            self.output_button,
            self.format_combo,
            self.settings_button,
        ):
            widget.setEnabled(not active)
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        summary = self._processor.summary()
        if summary.total == 0:
            text = "Fila vazia — nenhum histórico é mantido."
        else:
            text = (
                f"{summary.terminal} de {summary.total} finalizados — "
                f"{summary.completed} concluídos, {summary.failed} falharam, "
                f"{summary.cancelled} cancelados"
            )
        self.summary_label.setText(text)

    @Slot(str)
    def _on_worker_error(self, message: str) -> None:
        self.detail_label.setText(message)

    @Slot()
    def _on_thread_finished(self) -> None:
        thread = self._thread
        self._thread = None
        self._worker = None
        if thread is not None:
            thread.deleteLater()
        self.progress.hide()
        self._rebuild_table()
        self._refresh()
        if self._close_when_finished:
            self._close_when_finished = False
            self.close()

    @Slot()
    def _open_settings(self) -> None:
        self._create_settings_dialog().exec()

    def _create_settings_dialog(self) -> QDialog:
        dialog = QDialog(self)
        dialog.setObjectName("settingsDialog")
        dialog.setWindowTitle("Configurar OpenAI")
        dialog.setMinimumWidth(520)
        dialog.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dialog)
        layout.addWidget(self._settings_widget_factory())
        close_button = QPushButton("&Fechar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        return dialog

    @Slot()
    def _open_output(self) -> None:
        if self._output_directory is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._output_directory)))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls() and any(
            Path(url.toLocalFile()).suffix.lower() in _SUPPORTED for url in event.mimeData().urls()
        ):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        self.set_sources(
            Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()
        )
        event.acceptProposedAction()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            self._close_when_finished = True
            self._cancel_all()
            event.ignore()
            return
        self._processor.clear()
        event.accept()


def _failure_guidance(result: TranscribeSingleFileFailure) -> str:
    return f"{_FAILURE_GUIDANCE[result.category]} Código: {result.diagnostic_code}."


def _application_icon_path() -> Path:
    executable_root = Path(sys.executable).resolve().parent
    bundle_root = Path(getattr(sys, "_MEIPASS", executable_root))
    packaged = bundle_root / "assets" / "caleo-transcriber.png"
    if packaged.is_file():
        return packaged
    return Path(__file__).resolve().parents[3] / "assets" / "caleo-transcriber.png"
