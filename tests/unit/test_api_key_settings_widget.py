from PySide6.QtWidgets import QLabel, QLineEdit
from pytestqt.qtbot import QtBot
from tests.fakes.credential_store import InMemoryCredentialStore

from caleo_transcriber.application import ApiKeySettings
from caleo_transcriber.presentation.settings import ApiKeySettingsWidget

CANARY = "synthetic-ui-canary"


def _widget(qtbot: QtBot) -> ApiKeySettingsWidget:
    widget = ApiKeySettingsWidget(ApiKeySettings(InMemoryCredentialStore()))
    qtbot.addWidget(widget)
    widget.show()
    return widget


def test_widget_masks_saves_and_never_repeats_key(qtbot: QtBot) -> None:
    widget = _widget(qtbot)

    assert widget.key_input.echoMode() is QLineEdit.EchoMode.Password
    assert widget.status_label.text() == "Chave não configurada"

    widget.key_input.setText(CANARY)
    widget.save_button.click()

    assert widget.key_input.text() == ""
    assert widget.status_label.text() == "Chave configurada"
    visible_text = " ".join(label.text() for label in widget.findChildren(QLabel))
    assert CANARY not in visible_text
    assert "Chave salva" in widget.feedback_label.text()


def test_widget_tests_locally_and_removes_saved_key(qtbot: QtBot) -> None:
    widget = _widget(qtbot)
    widget.key_input.setText(CANARY)
    widget.save_button.click()

    widget.test_button.click()
    assert "somente ao transcrever" in widget.feedback_label.text()

    widget.remove_button.click()
    assert widget.status_label.text() == "Chave não configurada"
    assert widget.remove_button.isEnabled() is False


def test_widget_exposes_cloud_notice_and_keyboard_labels(qtbot: QtBot) -> None:
    widget = _widget(qtbot)
    labels = widget.findChildren(QLabel)

    assert "somente o áudio selecionado" in widget.cloud_notice.text()
    assert "pode gerar custo" in widget.cloud_notice.text()
    assert any(label.buddy() is widget.key_input for label in labels)
    assert widget.save_button.accessibleName()
    assert widget.test_button.accessibleName()
    assert widget.remove_button.accessibleName()
