import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.settings import data_folder


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path else data_folder() / "history.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL DEFAULT '',
                pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(history)")}
        if "kind" not in columns:
            self.connection.execute("ALTER TABLE history ADD COLUMN kind TEXT NOT NULL DEFAULT 'text'")
        if "image" not in columns:
            self.connection.execute("ALTER TABLE history ADD COLUMN image BLOB")
        if "last_used" not in columns:
            self.connection.execute("ALTER TABLE history ADD COLUMN last_used TEXT")
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_history_kind ON history(kind)")
        self.connection.commit()

    def add(self, content, limit=500, kind="text"):
        if kind == "text" and (not isinstance(content, str) or not content.strip()):
            return False
        if kind == "image" and (not isinstance(content, bytes) or not content):
            return False
        if kind not in ("text", "image"):
            return False
        column = "image" if kind == "image" else "content"
        existing = self.connection.execute(
            f"SELECT id FROM history WHERE kind = ? AND {column} = ? LIMIT 1",
            (kind, content),
        ).fetchone()
        now = datetime.now(timezone.utc).isoformat()
        if existing:
            self.connection.execute(
                "UPDATE history SET last_used = ?, created_at = ? WHERE id = ?",
                (now, now, existing["id"]),
            )
        else:
            self.connection.execute(
                "INSERT INTO history (content, image, kind, created_at, last_used) VALUES (?, ?, ?, ?, ?)",
                (content if kind == "text" else "", content if kind == "image" else None, kind, now, now),
            )
        self.trim(limit)
        return True

    def trim(self, limit):
        self.connection.execute("""
            DELETE FROM history WHERE pinned = 0 AND id NOT IN (
                SELECT id FROM history WHERE pinned = 0
                ORDER BY COALESCE(last_used, created_at) DESC, id DESC LIMIT ?
            )
        """, (max(1, int(limit)),))
        self.connection.commit()

    def get_all(self, search="", kind="all", favorites=False):
        conditions = []
        arguments = []
        if search:
            conditions.append("content LIKE ? ESCAPE '\\'")
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            arguments.append(f"%{escaped}%")
        if kind in ("text", "image", "link"):
            conditions.append("kind = ?" if kind != "link" else "kind = 'text' AND (content LIKE 'http://%' OR content LIKE 'https://%')")
            if kind != "link":
                arguments.append(kind)
        if favorites:
            conditions.append("pinned = 1")
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        return self.connection.execute(
            "SELECT id, content, pinned, created_at, kind, image, last_used FROM history" + where +
            " ORDER BY pinned DESC, COALESCE(last_used, created_at) DESC, id DESC", arguments,
        ).fetchall()

    def toggle_pin(self, item_id):
        self.connection.execute("UPDATE history SET pinned = 1 - pinned WHERE id = ?", (item_id,))
        self.connection.commit()

    def delete(self, item_id):
        self.connection.execute("DELETE FROM history WHERE id = ?", (item_id,))
        self.connection.commit()

    def clear(self, include_pinned=False):
        self.connection.execute("DELETE FROM history" if include_pinned else "DELETE FROM history WHERE pinned = 0")
        self.connection.commit()

    def delete_older_than(self, days):
        if not days:
            return
        cutoff = (datetime.now(timezone.utc) - timedelta(days=int(days))).isoformat()
        self.connection.execute(
            "DELETE FROM history WHERE pinned = 0 AND datetime(replace(COALESCE(last_used, created_at), 'T', ' ')) < datetime(?)",
            (cutoff,),
        )
        self.connection.commit()

    def count(self):
        return self.connection.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def close(self):
        self.connection.close()
