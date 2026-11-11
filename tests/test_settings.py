import tempfile
import unittest
from pathlib import Path

from src.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(Path(folder) / "settings.json")
            self.assertEqual(settings.values["history_limit"], 500)
            self.assertTrue(settings.values["monitoring"])

    def test_save_and_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            settings = Settings(path)
            settings.set("history_limit", 100)
            settings.set("monitoring", False)
            restored = Settings(path)
            self.assertEqual(restored.values["history_limit"], 100)
            self.assertFalse(restored.values["monitoring"])
