import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
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
        self.assertEqual(self.db.get_all()[0]["content"], "Hello")

    def test_skips_empty_text(self):
        self.assertFalse(self.db.add("  "))
        self.assertEqual(self.db.count(), 0)

    def test_repeated_text_moves_to_top(self):
        self.db.add("First")
        self.db.add("Second")
        self.db.add("First")
        self.assertEqual(self.db.count(), 2)
        self.assertEqual(self.db.get_all()[0]["content"], "First")

    def test_image_round_trip(self):
        self.assertTrue(self.db.add(b"fake png", kind="image"))
        row = self.db.get_all(kind="image")[0]
        self.assertEqual(row["image"], b"fake png")
        self.assertEqual(row["kind"], "image")

    def test_repeated_image_moves_to_top(self):
        self.db.add(b"image 1", kind="image")
        self.db.add(b"image 2", kind="image")
        self.db.add(b"image 1", kind="image")
        self.assertEqual(self.db.count(), 2)
        self.assertEqual(self.db.get_all(kind="image")[0]["image"], b"image 1")

    def test_search(self):
        self.db.add("Python")
        self.db.add("GitHub")
        self.assertEqual(len(self.db.get_all("Python")), 1)

    def test_filter_links(self):
        self.db.add("hello")
        self.db.add("https://example.com")
        self.assertEqual(len(self.db.get_all(kind="link")), 1)

    def test_pin_and_delete(self):
        self.db.add("Keep")
        item_id = self.db.get_all()[0]["id"]
        self.db.toggle_pin(item_id)
        self.assertEqual(len(self.db.get_all(favorites=True)), 1)
        self.db.delete(item_id)
        self.assertEqual(self.db.count(), 0)

    def test_clear_keeps_pinned(self):
        self.db.add("Keep")
        self.db.toggle_pin(self.db.get_all()[0]["id"])
        self.db.add("Remove")
        self.db.clear()
        self.assertEqual(self.db.count(), 1)

    def test_trim_keeps_pinned(self):
        self.db.add("Keep")
        self.db.toggle_pin(self.db.get_all()[0]["id"])
        self.db.add("First", limit=1)
        self.db.add("Second", limit=1)
        self.assertEqual(self.db.count(), 2)

    def test_search_literal_percent(self):
        self.db.add("50%")
        self.db.add("hello")
        self.assertEqual(len(self.db.get_all("%")), 1)

    def test_auto_delete_preserves_pinned(self):
        self.db.add("Old unpinned")
        self.db.add("Old pinned")
        self.db.toggle_pin(self.db.get_all()[0]["id"])
        old = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        self.db.connection.execute("UPDATE history SET created_at = ?, last_used = ?", (old, old))
        self.db.connection.commit()
        self.db.delete_older_than(30)
        self.assertEqual(self.db.count(), 1)
        self.assertEqual(self.db.get_all()[0]["content"], "Old pinned")

    def test_migrates_old_database(self):
        self.db.close()
        with closing(sqlite3.connect(self.db.path)) as connection:
            with connection:
                connection.execute("DROP TABLE history")
                connection.execute("CREATE TABLE history (id INTEGER PRIMARY KEY, content TEXT NOT NULL, pinned INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
                connection.execute("INSERT INTO history(content) VALUES ('Old copy')")
        self.db = Database(self.db.path)
        self.assertEqual(self.db.get_all()[0]["kind"], "text")
