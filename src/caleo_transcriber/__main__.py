"""Entrada gráfica do Caleo Transcriber."""

import sys

from keyring.backends.Windows import WinVaultKeyring
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication

from caleo_transcriber.bootstrap.main_window import create_main_window


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv if argv is None else argv)
    smoke_test = "--smoke-test" in arguments
    arguments = [argument for argument in arguments if argument != "--smoke-test"]
    QCoreApplication.setOrganizationName("caleo-hub")
    QCoreApplication.setApplicationName("Caleo Transcriber")
    application = QApplication(arguments)
    window = create_main_window()
    window.show()
    if smoke_test:
        if WinVaultKeyring.priority <= 0:
            return 2
        QTimer.singleShot(1_000, application.quit)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
