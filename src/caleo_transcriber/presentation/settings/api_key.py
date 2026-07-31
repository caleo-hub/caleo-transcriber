"""Tela acessível para a credencial da OpenAI."""

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from caleo_transcriber.application import ApiKeySettings, CredentialStoreError


class ApiKeySettingsWidget(QWidget):
    """Edita a chave sem reapresentar o segredo armazenado."""

    def __init__(self, settings: ApiKeySettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Configurar OpenAI")

        self.cloud_notice = QLabel(
            "OpenAI (cloud): somente o áudio selecionado será enviado e pode gerar custo."
        )
        self.cloud_notice.setWordWrap(True)
        self.cloud_notice.setAccessibleName("Aviso do modo OpenAI cloud")

        self.status_label = QLabel()
        self.status_label.setAccessibleName("Estado da chave OpenAI")

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Cole uma nova chave")
        self.key_input.setAccessibleName("Nova chave da API OpenAI")

        key_label = QLabel("&Nova chave:")
        key_label.setBuddy(self.key_input)

        self.save_button = QPushButton("&Salvar ou substituir")
        self.test_button = QPushButton("&Testar localmente")
        self.remove_button = QPushButton("&Remover")
        self.save_button.setAccessibleName("Salvar ou substituir chave OpenAI")
        self.test_button.setAccessibleName("Testar chave OpenAI localmente")
        self.remove_button.setAccessibleName("Remover chave OpenAI")

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setAccessibleName("Resultado da operação com a chave")

        form = QFormLayout()
        form.addRow(key_label, self.key_input)

        actions = QHBoxLayout()
        actions.addWidget(self.save_button)
        actions.addWidget(self.test_button)
        actions.addWidget(self.remove_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.cloud_notice)
        layout.addWidget(self.status_label)
        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.feedback_label)

        self.save_button.clicked.connect(self._save)
        self.test_button.clicked.connect(self._test_locally)
        self.remove_button.clicked.connect(self._remove)
        self._refresh_status()

    def _refresh_status(self) -> None:
        try:
            configured = self._settings.is_configured()
        except CredentialStoreError:
            self.status_label.setText("Não foi possível consultar o armazenamento protegido.")
            self.remove_button.setEnabled(False)
            return
        self.status_label.setText("Chave configurada" if configured else "Chave não configurada")
        self.remove_button.setEnabled(configured)

    def _save(self) -> None:
        try:
            result = self._settings.save(self.key_input.text())
        except CredentialStoreError:
            self.feedback_label.setText("Não foi possível salvar no armazenamento protegido.")
            return
        self.feedback_label.setText(
            "Chave salva no armazenamento protegido." if result.valid else result.message
        )
        if result.valid:
            self.key_input.clear()
            self._refresh_status()

    def _test_locally(self) -> None:
        try:
            candidate = self.key_input.text()
            result = (
                self._settings.validate_candidate(candidate)
                if candidate
                else self._settings.validate_saved()
            )
        except CredentialStoreError:
            self.feedback_label.setText("Não foi possível consultar o armazenamento protegido.")
            return
        self.feedback_label.setText(result.message)

    def _remove(self) -> None:
        try:
            removed = self._settings.remove()
        except CredentialStoreError:
            self.feedback_label.setText("Não foi possível remover do armazenamento protegido.")
            return
        self.key_input.clear()
        self.feedback_label.setText(
            "Chave removida." if removed else "Nenhuma chave estava configurada."
        )
        self._refresh_status()
