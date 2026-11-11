import unittest
from unittest.mock import Mock

from src.clipboard import ClipboardWatcher


class ClipboardTests(unittest.TestCase):
    def test_new_text_is_reported_once(self):
        root = Mock()
        root.clipboard_get.return_value = "Hello"
        on_copy = Mock()
        watcher = ClipboardWatcher(root, on_copy)
        watcher.check()
        watcher.check()
        on_copy.assert_called_once_with("Hello")

    def test_paused_monitoring_skips_text(self):
        root = Mock()
        root.clipboard_get.return_value = "Hello"
        on_copy = Mock()
        watcher = ClipboardWatcher(root, on_copy)
        watcher.set_enabled(False)
        watcher.check()
        on_copy.assert_not_called()
