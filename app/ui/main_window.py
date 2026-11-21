from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from app.config import APP_NAME, APP_VERSION, Paths


class MainWindow(QMainWindow):
    def __init__(self, paths: Paths) -> None:
        super().__init__()
        self.paths = paths
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 800)
        self.setMinimumSize(960, 640)

        self.status_label = QLabel(self._status_text())
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_label = QLabel(f"{APP_NAME} {APP_VERSION}")
        self.version_label.setObjectName("versionLabel")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        layout.addWidget(self.version_label)
        layout.addStretch(1)
        self.setCentralWidget(container)

    def _status_text(self) -> str:
        missing = self.paths.missing_models()
        if missing:
            return "Models missing: " + ", ".join(missing)
        return "Ready"
