#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
    echo "Create the virtual environment first: python3 -m venv .venv"
    exit 1
fi
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m PyInstaller --noconfirm --clean --windowed --name MultiCopy --paths . --add-data "src/assets/multicopy-logo.png:src/assets" run.py
echo "Build created: dist/MultiCopy.app"
