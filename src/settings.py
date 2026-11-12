import json
import os
import sys
from pathlib import Path


def data_folder():
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MultiCopy"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "MultiCopy"
    return Path.home() / ".multicopy"


class Settings:
    DEFAULTS = {"history_limit": 500, "monitoring": True, "auto_delete_days": 0}

    def __init__(self, path=None):
        self.path = Path(path) if path else data_folder() / "settings.json"
        self.values = self.DEFAULTS.copy()
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                self.values.update({k: v for k, v in saved.items() if k in self.DEFAULTS})
        except (OSError, ValueError):
            pass
        self.values["history_limit"] = self._valid_limit(self.values["history_limit"])
        self.values["monitoring"] = self.values["monitoring"] is not False
        self.values["auto_delete_days"] = self._valid_days(self.values["auto_delete_days"])

    @staticmethod
    def _valid_limit(value):
        try:
            return max(50, min(int(value), 5000))
        except (TypeError, ValueError):
            return 500

    @staticmethod
    def _valid_days(value):
        try:
            days = int(value)
            return days if days in (0, 1, 7, 30, 90) else 0
        except (TypeError, ValueError):
            return 0

    def set(self, key, value):
        if key == "history_limit":
            value = self._valid_limit(value)
        elif key == "monitoring":
            value = bool(value)
        elif key == "auto_delete_days":
            value = self._valid_days(value)
        else:
            raise KeyError(key)
        self.values[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
        temporary.replace(self.path)
