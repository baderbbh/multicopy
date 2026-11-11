import sqlite3
from pathlib import Path

from src.settings import data_folder


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path else data_folder() / "history.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def add(self, content, limit=500):
        if not isinstance(content, str) or not content.strip():
            return False
        last = self.connection.execute(
            "SELECT content FROM history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last and last[0] == content:
            return False
        self.connection.execute("INSERT INTO history (content) VALUES (?)", (content,))
        self.trim(limit)
        return True

    def trim(self, limit):
        limit = max(1, int(limit))
        self.connection.execute("""
            DELETE FROM history
            WHERE pinned = 0 AND id NOT IN (
                SELECT id FROM history WHERE pinned = 0
                ORDER BY id DESC LIMIT ?
            )
        """, (limit,))
        self.connection.commit()

    def get_all(self, search=""):
        return self.connection.execute("""
            SELECT id, content, pinned, created_at FROM history
            WHERE content LIKE ? ESCAPE '\\'
            ORDER BY pinned DESC, id DESC
        """, ("%" + search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%",)).fetchall()

    def toggle_pin(self, item_id):
        self.connection.execute("""
            UPDATE history SET pinned = 1 - pinned WHERE id = ?
        """, (item_id,))
        self.connection.commit()

    def delete(self, item_id):
        self.connection.execute("DELETE FROM history WHERE id = ?", (item_id,))
        self.connection.commit()

    def clear(self, include_pinned=False):
        if include_pinned:
            self.connection.execute("DELETE FROM history")
        else:
            self.connection.execute("DELETE FROM history WHERE pinned = 0")
        self.connection.commit()

    def count(self):
        return self.connection.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def close(self):
        self.connection.close()
