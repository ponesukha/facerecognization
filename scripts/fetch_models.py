from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import cv2

BASE_URL = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models"
MODEL_SOURCES = {
    "face_detection_yunet_2023mar.onnx": "face_detection_yunet",
    "face_recognition_sface_2021dec.onnx": "face_recognition_sface",
}
MODELS = {name: f"{BASE_URL}/{folder}/{name}" for name, folder in MODEL_SOURCES.items()}
DEFAULT_TARGET = Path(__file__).resolve().parent.parent / "models"


def validate(path: Path) -> None:
    if "yunet" in path.name:
        cv2.FaceDetectorYN.create(str(path), "", (320, 320))
    else:
        cv2.FaceRecognizerSF.create(str(path), "")


def fetch(name: str, url: str, target: Path, force: bool) -> Path:
    destination = target / name
    if destination.is_file() and not force:
        validate(destination)
        return destination
    partial = destination.with_name(f"{destination.stem}.download.onnx")
    try:
        urllib.request.urlretrieve(url, partial)
        validate(partial)
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    args.target.mkdir(parents=True, exist_ok=True)
    for name, url in MODELS.items():
        path = fetch(name, url, args.target, args.force)
        print(f"{path.name}  {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
