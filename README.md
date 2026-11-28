# MRO Face

Face recognition desktop app for Mon Refugee Organization staff. See [docs/PLAN.md](docs/PLAN.md).

## Setup (macOS, Apple Silicon)

```bash
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/fetch_models.py
```

## Run

```bash
python -m app
```

## Test

```bash
ruff check .
pytest
```

## Build

```bash
pyinstaller packaging/mro_face.spec --noconfirm --clean
```
