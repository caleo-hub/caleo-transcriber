"""Entrada gráfica do Caleo Transcriber."""

import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from caleo_transcriber.bootstrap.main_window import create_main_window


def main() -> int:
    QCoreApplication.setOrganizationName("caleo-hub")
    QCoreApplication.setApplicationName("Caleo Transcriber")
    application = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
