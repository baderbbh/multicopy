import sys
from pathlib import Path


def base_path():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset_path(*parts):
    return base_path().joinpath(*parts)
