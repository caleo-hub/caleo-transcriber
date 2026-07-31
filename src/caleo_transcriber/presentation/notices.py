"""Preferência não secreta para o aviso inicial do modo cloud."""

from typing import Protocol, runtime_checkable

from PySide6.QtCore import QSettings


@runtime_checkable
class CloudNoticePolicy(Protocol):
    def should_show(self) -> bool: ...

    def mark_shown(self) -> None: ...


class QSettingsCloudNoticePolicy:
    _KEY = "privacy/openai-cloud-notice-shown"

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings or QSettings()

    def should_show(self) -> bool:
        return not self._settings.value(self._KEY, False, type=bool)

    def mark_shown(self) -> None:
        self._settings.setValue(self._KEY, True)
        self._settings.sync()
