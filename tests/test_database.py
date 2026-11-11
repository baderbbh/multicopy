import tempfile
import unittest
from pathlib import Path

from src.database import Database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.folder.name) / "history.db")

    def tearDown(self):
        self.db.close()
        self.folder.cleanup()

    def test_saves_text(self):
        self.assertTrue(self.db.add("Hello"))
        self.assertEqual(self.db.get_all()[0][1], "Hello")

    def test_skips_empty_text(self):
        self.assertFalse(self.db.add("  "))
        self.assertEqual(self.db.count(), 0)

    def test_skips_consecutive_duplicates(self):
        self.db.add("Hello")
        self.assertFalse(self.db.add("Hello"))
        self.assertEqual(self.db.count(), 1)

    def test_search(self):
        self.db.add("Python")
        self.db.add("GitHub")
        self.assertEqual(len(self.db.get_all("Python")), 1)

    def test_pin_and_delete(self):
        self.db.add("Keep")
        item_id = self.db.get_all()[0][0]
        self.db.toggle_pin(item_id)
        self.assertEqual(self.db.get_all()[0][2], 1)
        self.db.delete(item_id)
        self.assertEqual(self.db.count(), 0)

    def test_clear_keeps_pinned(self):
        self.db.add("Keep")
        self.db.toggle_pin(self.db.get_all()[0][0])
        self.db.add("Remove")
        self.db.clear()
        self.assertEqual(self.db.count(), 1)

    def test_trim_keeps_pinned(self):
        self.db.add("Keep")
        self.db.toggle_pin(self.db.get_all()[0][0])
        self.db.add("First", limit=1)
        self.db.add("Second", limit=1)
        self.assertEqual(self.db.count(), 2)

    def test_search_literal_percent(self):
        self.db.add("50%")
        self.db.add("hello")
        self.assertEqual(len(self.db.get_all("%")), 1)
