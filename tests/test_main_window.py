from pathlib import Path

from app.config import APP_NAME, DETECTOR_MODEL, RECOGNIZER_MODEL, Paths
from app.ui.main_window import MainWindow


def build_paths(tmp_path: Path) -> Paths:
    models = tmp_path / "models"
    models.mkdir()
    return Paths.default(data_root=tmp_path / "data", models_root=models).ensure()


def test_window_reports_missing_models(qtbot, tmp_path: Path) -> None:
    window = MainWindow(build_paths(tmp_path))
    qtbot.addWidget(window)
    assert window.windowTitle() == APP_NAME
    assert window.status_label.text().startswith("Models missing")


def test_window_ready_when_models_present(qtbot, tmp_path: Path) -> None:
    paths = build_paths(tmp_path)
    (paths.models / DETECTOR_MODEL).write_bytes(b"x")
    (paths.models / RECOGNIZER_MODEL).write_bytes(b"x")
    window = MainWindow(paths)
    qtbot.addWidget(window)
    assert window.status_label.text() == "Ready"
