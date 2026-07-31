"""Composição da tela de configuração."""

from caleo_transcriber.adapters.credentials import WindowsCredentialStore
from caleo_transcriber.application import ApiKeySettings
from caleo_transcriber.presentation.settings import ApiKeySettingsWidget


def create_api_key_settings_widget() -> ApiKeySettingsWidget:
    """Monta a tela com o armazenamento protegido do Windows."""
    return ApiKeySettingsWidget(ApiKeySettings(WindowsCredentialStore()))
