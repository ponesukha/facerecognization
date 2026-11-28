from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.config import APP_NAME, APP_ORG, APP_VERSION, Paths
from app.ui.main_window import MainWindow


def create_application(argv: list[str]) -> QApplication:
    app = QApplication.instance() or QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(APP_ORG)
    app.setApplicationVersion(APP_VERSION)
    return app


def main() -> int:
    app = create_application(sys.argv)
    paths = Paths.default().ensure()
    window = MainWindow(paths)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
