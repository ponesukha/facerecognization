from pathlib import Path

from app.config import DETECTOR_MODEL, RECOGNIZER_MODEL, Paths


def test_paths_are_created(tmp_path: Path) -> None:
    paths = Paths.default(data_root=tmp_path / "data", models_root=tmp_path / "models").ensure()
    assert paths.data.is_dir()
    assert paths.thumbnails.is_dir()
    assert paths.logs.is_dir()
    assert paths.database.parent == paths.data


def test_missing_models_reported(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    paths = Paths.default(data_root=tmp_path / "data", models_root=models)
    assert paths.missing_models() == [DETECTOR_MODEL, RECOGNIZER_MODEL]
    (models / DETECTOR_MODEL).write_bytes(b"x")
    (models / RECOGNIZER_MODEL).write_bytes(b"x")
    assert paths.missing_models() == []
