import json
import os
from pathlib import Path


def data_folder():
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "MultiCopy"
    return Path.home() / ".multicopy"


class Settings:
    DEFAULTS = {"history_limit": 500, "monitoring": True}

    def __init__(self, path=None):
        self.path = Path(path) if path else data_folder() / "settings.json"
        self.values = self.DEFAULTS.copy()
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                self.values.update(saved)
        except (OSError, ValueError):
            pass
        self.values["history_limit"] = self._valid_limit(self.values.get("history_limit"))
        self.values["monitoring"] = self.values.get("monitoring") is not False

    @staticmethod
    def _valid_limit(value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            return 500
        return max(50, min(value, 5000))

    def set(self, key, value):
        if key == "history_limit":
            value = self._valid_limit(value)
        elif key == "monitoring":
            value = bool(value)
        else:
            raise KeyError(key)
        self.values[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
        temp.replace(self.path)
