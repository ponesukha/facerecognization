from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "MRO Face"
APP_ORG = "Mon Refugee Organization"
APP_VERSION = "0.1.0"

DETECTOR_MODEL = "face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = "face_recognition_sface_2021dec.onnx"
REQUIRED_MODELS = (DETECTOR_MODEL, RECOGNIZER_MODEL)


def resource_root() -> Path:
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return Path(bundled)
    return Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    data: Path
    database: Path
    thumbnails: Path
    logs: Path
    models: Path

    @classmethod
    def default(cls, data_root: Path | None = None, models_root: Path | None = None) -> Paths:
        data = data_root or Path(user_data_dir(APP_NAME, appauthor=False))
        return cls(
            data=data,
            database=data / "mro_face.db",
            thumbnails=data / "thumbnails",
            logs=data / "logs",
            models=models_root or resource_root() / "models",
        )

    def ensure(self) -> Paths:
        for directory in (self.data, self.thumbnails, self.logs):
            directory.mkdir(parents=True, exist_ok=True)
        return self

    def missing_models(self) -> list[str]:
        return [name for name in REQUIRED_MODELS if not (self.models / name).is_file()]
