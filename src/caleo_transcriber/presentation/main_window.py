"""Janela principal da primeira fatia de transcrição."""

import uuid
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from caleo_transcriber import __version__
from caleo_transcriber.application import (
    AttemptEvent,
    TranscribeSingleFileCommand,
    TranscribeSingleFileFailure,
    TranscribeSingleFileSuccess,
    TranscribeSingleFileUseCase,
)
from caleo_transcriber.domain import AttemptState
from caleo_transcriber.presentation.notices import CloudNoticePolicy
from caleo_transcriber.presentation.worker import CancellationToken, TranscriptionWorker

_ACTIVE_STATES = {
    AttemptState.PREPARING,
    AttemptState.TRANSCRIBING,
    AttemptState.SAVING,
    AttemptState.CANCELLING,
}
_STATE_TEXT = {
    AttemptState.READY: "Pronto para iniciar",
    AttemptState.PREPARING: "Preparando somente o áudio...",
    AttemptState.TRANSCRIBING: "Transcrevendo pela OpenAI...",
    AttemptState.SAVING: "Salvando o arquivo TXT...",
    AttemptState.COMPLETED: "Transcrição concluída",
    AttemptState.FAILED: "Não foi possível concluir",
    AttemptState.CANCELLING: "Cancelando com segurança...",
    AttemptState.CANCELLED: "Transcrição cancelada",
}
_FAILURE_TEXT = {
    "invalid_input": "O arquivo não é válido. Escolha MP4, MP3 ou WAV com até 30 minutos.",
    "unsupported_media": "Formato não suportado. Escolha MP4, MP3 ou WAV.",
    "credential": "Configure ou substitua sua chave da OpenAI e tente novamente.",
    "network": "Falha de rede ou tempo esgotado. Verifique a conexão e tente novamente.",
    "rate_limit": "A OpenAI limitou temporariamente as solicitações. Tente mais tarde.",
    "provider": "A transcrição não foi concluída pela OpenAI. Tente novamente.",
    "cancelled": "O trabalho foi cancelado e os temporários foram descartados.",
    "output": "Não foi possível salvar o TXT. Escolha outro destino e tente novamente.",
}


class QtAttemptEvents(QObject):
    event_published = Signal(object)

    def publish(self, event: AttemptEvent) -> None:
        self.event_published.emit(event)


class MainWindow(QMainWindow):
    def __init__(
        self,
        use_case: TranscribeSingleFileUseCase,
        events: QtAttemptEvents,
        workspace: Path,
        settings_widget_factory: Callable[[], QWidget],
        notice_policy: CloudNoticePolicy,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._events = events
        self._workspace = workspace
        self._settings_widget_factory = settings_widget_factory
        self._notice_policy = notice_policy
        self._source: Path | None = None
        self._output_directory: Path | None = None
        self._last_output: Path | None = None
        self._thread: QThread | None = None
        self._worker: TranscriptionWorker | None = None
        self._cancellation: CancellationToken | None = None
        self._close_when_finished = False

        self.setWindowTitle(f"Caleo Transcriber {__version__}")
        self.setMinimumSize(760, 560)
        self.resize(860, 620)
        self._build_ui()
        self._apply_style()
        self._events.event_published.connect(self._on_attempt_event)
        self._refresh_actions()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel(f"Caleo Transcriber  {__version__}")
        title.setObjectName("title")
        subtitle = QLabel("Transforme áudio ou vídeo em texto, sem complicação.")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        self.settings_button = QPushButton("&Configurar chave")
        self.settings_button.setAccessibleName("Configurar chave da OpenAI")
        self.settings_button.clicked.connect(self._open_settings)
        header.addWidget(self.settings_button)
        root.addLayout(header)

        cloud_card = QFrame()
        cloud_card.setObjectName("cloudCard")
        cloud_layout = QHBoxLayout(cloud_card)
        cloud_title = QLabel("OpenAI (cloud)")
        cloud_title.setObjectName("cloudTitle")
        cloud_text = QLabel("Envia somente o áudio selecionado e pode gerar custo.")
        cloud_text.setWordWrap(True)
        cloud_text.setAccessibleName("Aviso permanente do modo OpenAI cloud")
        cloud_layout.addWidget(cloud_title)
        cloud_layout.addWidget(cloud_text, 1)
        root.addWidget(cloud_card)

        selection_card = QFrame()
        selection_card.setObjectName("card")
        grid = QGridLayout(selection_card)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(14)

        source_label = QLabel("&Arquivo de áudio ou vídeo")
        self.source_field = QLineEdit()
        self.source_field.setReadOnly(True)
        self.source_field.setPlaceholderText("Selecione um arquivo MP4, MP3 ou WAV")
        self.source_field.setAccessibleName("Arquivo selecionado")
        source_label.setBuddy(self.source_field)
        self.source_button = QPushButton("&Selecionar arquivo")
        self.source_button.clicked.connect(self._choose_source)

        output_label = QLabel("&Pasta de saída")
        self.output_field = QLineEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setPlaceholderText("Escolha onde salvar o arquivo TXT")
        self.output_field.setAccessibleName("Pasta de saída selecionada")
        output_label.setBuddy(self.output_field)
        self.output_button = QPushButton("Escolher &pasta")
        self.output_button.clicked.connect(self._choose_output)

        format_label = QLabel("Formato de saída")
        format_value = QLabel("TXT  •  UTF-8  •  sem sobrescrever arquivos")
        format_value.setObjectName("muted")

        grid.addWidget(source_label, 0, 0, 1, 2)
        grid.addWidget(self.source_field, 1, 0)
        grid.addWidget(self.source_button, 1, 1)
        grid.addWidget(output_label, 2, 0, 1, 2)
        grid.addWidget(self.output_field, 3, 0)
        grid.addWidget(self.output_button, 3, 1)
        grid.addWidget(format_label, 4, 0)
        grid.addWidget(format_value, 4, 1)
        grid.setColumnStretch(0, 1)
        root.addWidget(selection_card)

        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 18, 20, 18)
        status_heading = QLabel("Estado do trabalho")
        status_heading.setObjectName("sectionTitle")
        self.status_label = QLabel("Selecione o arquivo e a pasta de saída.")
        self.status_label.setWordWrap(True)
        self.status_label.setAccessibleName("Estado atual da transcrição")
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setAccessibleName("Atividade da transcrição")
        self.progress.hide()
        self.detail_label = QLabel("Nenhum histórico é mantido.")
        self.detail_label.setObjectName("muted")
        self.detail_label.setWordWrap(True)
        status_layout.addWidget(status_heading)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress)
        status_layout.addWidget(self.detail_label)
        root.addWidget(status_card)
        root.addStretch()

        actions = QHBoxLayout()
        self.start_button = QPushButton("&Iniciar transcrição")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self._start)
        self.cancel_button = QPushButton("&Cancelar")
        self.cancel_button.clicked.connect(self._cancel)
        self.retry_button = QPushButton("&Tentar novamente")
        self.retry_button.clicked.connect(self._start)
        self.open_output_button = QPushButton("&Abrir pasta de saída")
        self.open_output_button.clicked.connect(self._open_output)
        actions.addWidget(self.start_button)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.retry_button)
        actions.addStretch()
        actions.addWidget(self.open_output_button)
        root.addLayout(actions)
        self.setCentralWidget(central)

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget { font-family: "Segoe UI"; font-size: 13px; color: #152238; }
            QMainWindow { background: #F4F7FB; color: #152238; }
            QLabel#title { font-size: 26px; font-weight: 700; color: #102A43; }
            QLabel#subtitle, QLabel#muted { color: #62748A; }
            QLabel#sectionTitle { font-size: 15px; font-weight: 700; color: #243B53; }
            QFrame#card { background: white; border: 1px solid #D9E2EC; border-radius: 10px; }
            QFrame#cloudCard {
                background: #E8F3FF;
                border: 1px solid #9BC7F5;
                border-radius: 10px;
            }
            QLabel#cloudTitle { font-weight: 700; color: #0B5CAD; }
            QLineEdit {
                background: #FFFFFF;
                border: 1px solid #BCCCDC;
                border-radius: 6px;
                padding: 9px;
            }
            QLineEdit:focus { border: 2px solid #1677C8; }
            QPushButton {
                background: #FFFFFF;
                border: 1px solid #9FB3C8;
                border-radius: 6px;
                padding: 9px 13px;
            }
            QPushButton:hover { background: #EDF2F7; }
            QPushButton:focus { border: 2px solid #1677C8; }
            QPushButton:disabled { color: #9AA9B8; background: #EEF2F6; }
            QPushButton#primaryButton {
                background: #1261A0;
                color: white;
                border-color: #1261A0;
                font-weight: 700;
            }
            QPushButton#primaryButton:hover { background: #0B4F86; }
            QProgressBar {
                min-height: 8px;
                max-height: 8px;
                border: none;
                border-radius: 4px;
                background: #D9E2EC;
            }
            QProgressBar::chunk { background: #1677C8; border-radius: 4px; }
            """
        )

    def set_source(self, source: Path) -> None:
        self._source = source
        self.source_field.setText(str(source))
        self._show_ready_if_configured()

    def set_output_directory(self, directory: Path) -> None:
        self._output_directory = directory
        self.output_field.setText(str(directory))
        self._show_ready_if_configured()

    @Slot()
    def _choose_source(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar áudio ou vídeo",
            "",
            "Mídia suportada (*.mp4 *.mp3 *.wav)",
        )
        if filename:
            self.set_source(Path(filename))

    @Slot()
    def _choose_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Escolher pasta de saída")
        if directory:
            self.set_output_directory(Path(directory))

    def _show_ready_if_configured(self) -> None:
        if self._source is not None and self._output_directory is not None:
            self.status_label.setText(_STATE_TEXT[AttemptState.READY])
            self.detail_label.setText(
                "Revise o arquivo, o destino e o aviso cloud antes de iniciar."
            )
        self._refresh_actions()

    @Slot()
    def _start(self) -> None:
        if self._source is None or self._output_directory is None or self._thread is not None:
            return
        if self._notice_policy.should_show():
            QMessageBox.information(
                self,
                "Antes de usar a OpenAI",
                "Este modo envia somente o áudio preparado para a OpenAI "
                "e pode gerar custo na sua conta.",
            )
            self._notice_policy.mark_shown()

        self._last_output = None
        cancellation = CancellationToken()
        command = TranscribeSingleFileCommand(
            uuid.uuid4().hex,
            self._source,
            self._output_directory,
            self._workspace,
        )
        thread = QThread(self)
        worker = TranscriptionWorker(self._use_case, command, cancellation)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.result_ready.connect(self._on_result)
        worker.safe_error.connect(self._on_worker_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        self._thread = thread
        self._worker = worker
        self._cancellation = cancellation
        self.status_label.setText("Iniciando trabalho...")
        self.detail_label.setText(
            "A etapa atual aparecerá aqui; o tempo depende do arquivo e da rede."
        )
        self.progress.setRange(0, 0)
        self.progress.show()
        self._refresh_actions()
        thread.start()

    @Slot()
    def _cancel(self) -> None:
        if self._cancellation is not None:
            self._cancellation.request()
            self.status_label.setText(_STATE_TEXT[AttemptState.CANCELLING])
            self.cancel_button.setEnabled(False)

    @Slot(object)
    def _on_attempt_event(self, value: object) -> None:
        if not isinstance(value, AttemptEvent):
            return
        self.status_label.setText(_STATE_TEXT[value.state])
        if value.state in _ACTIVE_STATES:
            self.progress.setRange(0, 0)
            self.progress.show()
        elif value.state is AttemptState.COMPLETED:
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
            self.progress.show()
        else:
            self.progress.hide()

    @Slot(object)
    def _on_result(self, value: object) -> None:
        if isinstance(value, TranscribeSingleFileSuccess):
            self._last_output = value.output_path
            self.status_label.setText(_STATE_TEXT[AttemptState.COMPLETED])
            self.detail_label.setText(
                "TXT vazio: nenhuma fala foi detectada."
                if "no_speech_detected" in value.warnings
                else f"Arquivo criado: {value.output_path.name}"
            )
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
            self.progress.show()
        elif isinstance(value, TranscribeSingleFileFailure):
            self.status_label.setText(_STATE_TEXT[value.state])
            self.detail_label.setText(_FAILURE_TEXT[value.category.value])
            self.progress.hide()

    @Slot(str)
    def _on_worker_error(self, message: str) -> None:
        self.status_label.setText(_STATE_TEXT[AttemptState.FAILED])
        self.detail_label.setText(message)
        self.progress.hide()

    @Slot()
    def _on_thread_finished(self) -> None:
        thread = self._thread
        self._thread = None
        self._worker = None
        self._cancellation = None
        if thread is not None:
            thread.deleteLater()
        self._refresh_actions()
        if self._close_when_finished:
            self._close_when_finished = False
            self.close()

    def _refresh_actions(self) -> None:
        configured = self._source is not None and self._output_directory is not None
        active = self._thread is not None
        failed_or_cancelled = self.status_label.text() in {
            _STATE_TEXT[AttemptState.FAILED],
            _STATE_TEXT[AttemptState.CANCELLED],
        }
        self.start_button.setEnabled(configured and not active)
        self.source_button.setEnabled(not active)
        self.output_button.setEnabled(not active)
        self.settings_button.setEnabled(not active)
        self.cancel_button.setEnabled(active)
        self.retry_button.setEnabled(configured and not active and failed_or_cancelled)
        self.open_output_button.setEnabled(self._last_output is not None and not active)

    @Slot()
    def _open_settings(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar OpenAI")
        layout = QVBoxLayout(dialog)
        layout.addWidget(self._settings_widget_factory())
        close_button = QPushButton("&Fechar")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec()

    @Slot()
    def _open_output(self) -> None:
        if self._last_output is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output.parent)))

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            self._close_when_finished = True
            self._cancel()
            event.ignore()
            return
        event.accept()
