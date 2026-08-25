"""Local SQLite storage for Rhodium: browsing history and recent searches.

All suggestion data for Phase 1 comes from this database. It is fully offline.
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_DB_PATH = Path.home() / ".rhodium" / "rhodium.db"

# Schemes that must never end up in history / suggestions.
_BLOCKED_SCHEMES = ("rhodium", "about", "data", "javascript", "chrome", "view-source", "blob")
_ALLOWED_SCHEMES = ("http", "https", "file")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def is_recordable_url(url: str) -> bool:
    """True when a URL is valid and safe to store in local history."""
    url = (url or "").strip()
    if not url:
        return False
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme.lower() not in _ALLOWED_SCHEMES:
        return False
    if parts.scheme.lower() != "file" and not parts.netloc:
        return False
    return True


class RhodiumDatabase:
    """Small thread-safe wrapper around Rhodium's local SQLite database."""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    # ── Setup ────────────────────────────────────────────────────────────────
    def _init_schema(self):
        with self._lock, self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    url          TEXT PRIMARY KEY,
                    title        TEXT NOT NULL DEFAULT '',
                    visit_count  INTEGER NOT NULL DEFAULT 1,
                    last_visited TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    query         TEXT PRIMARY KEY,
                    search_count  INTEGER NOT NULL DEFAULT 1,
                    last_searched TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_history_visited ON history(last_visited)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_search_searched ON search_history(last_searched)"
            )

    def close(self):
        with self._lock:
            self._conn.close()

    # ── History recording ────────────────────────────────────────────────────
    def record_visit(self, url: str, title: str = ""):
        """Insert or update a history row. Repeated visits bump visit_count."""
        url = (url or "").strip()
        if not is_recordable_url(url):
            return
        title = (title or "").strip()
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO history (url, title, visit_count, last_visited)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(url) DO UPDATE SET
                    visit_count  = visit_count + 1,
                    last_visited = excluded.last_visited,
                    title = CASE
                        WHEN excluded.title != '' THEN excluded.title
                        ELSE history.title
                    END
                """,
                (url, title, now_iso()),
            )

    # ── Search history recording ─────────────────────────────────────────────
    def record_search(self, query: str):
        """Insert or update a recent-search row."""
        query = (query or "").strip()
        if not query:
            return
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT INTO search_history (query, search_count, last_searched)
                VALUES (?, 1, ?)
                ON CONFLICT(query) DO UPDATE SET
                    search_count  = search_count + 1,
                    last_searched = excluded.last_searched
                """,
                (query, now_iso()),
            )

    # ── Queries (for SuggestionController) ───────────────────────────────────
    @staticmethod
    def _like_pattern(query: str) -> str:
        escaped = (
            query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        return f"%{escaped}%"

    def search_urls(self, query: str, limit: int = 60):
        """History rows whose URL or title contains the query (case-insensitive)."""
        pattern = self._like_pattern(query)
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT url, title, visit_count, last_visited FROM history
                WHERE title LIKE ? ESCAPE '\\'
                   OR url LIKE ? ESCAPE '\\'
                ORDER BY last_visited DESC
                LIMIT ?
                """,
                (pattern, pattern, limit),
            ).fetchall()
        return [
            {"url": r[0], "title": r[1], "visit_count": r[2], "last_visited": r[3]}
            for r in rows
        ]

    def search_searches(self, query: str, limit: int = 20):
        """Recent searches containing the query (case-insensitive)."""
        pattern = self._like_pattern(query)
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT query, search_count, last_searched FROM search_history
                WHERE query LIKE ? ESCAPE '\\'
                ORDER BY last_searched DESC
                LIMIT ?
                """,
                (pattern, limit),
            ).fetchall()
        return [
            {"query": r[0], "search_count": r[1], "last_searched": r[2]}
            for r in rows
        ]

    def recent_searches(self, limit: int = 10):
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT query, search_count, last_searched FROM search_history
                ORDER BY last_searched DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {"query": r[0], "search_count": r[1], "last_searched": r[2]}
            for r in rows
        ]

    def history_row_count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    # ── One-time migration from the legacy JSON history file ────────────────
    def migrate_json_history(self, json_path: Path):
        """Import legacy ~/.rhodium/history.json entries once, if DB is empty."""
        json_path = Path(json_path)
        if not json_path.exists() or self.history_row_count() > 0:
            return 0
        try:
            import json

            entries = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return 0

        imported = 0
        with self._lock, self._conn:
            for entry in entries if isinstance(entries, list) else []:
                url = (entry.get("url") or "").strip()
                if not is_recordable_url(url):
                    continue
                title = (entry.get("title") or "").strip()
                visited = entry.get("timestamp") or now_iso()
                self._conn.execute(
                    """
                    INSERT INTO history (url, title, visit_count, last_visited)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        visit_count  = visit_count + 1,
                        last_visited = MAX(history.last_visited, excluded.last_visited),
                        title = CASE
                            WHEN excluded.title != '' THEN excluded.title
                            ELSE history.title
                        END
                    """,
                    (url, title, visited),
                )
                imported += 1
        return imported


_shared_db = None


def get_database() -> RhodiumDatabase:
    """Process-wide shared database instance (safe across browser windows)."""
    global _shared_db
    if _shared_db is None:
        _shared_db = RhodiumDatabase()
        _shared_db.migrate_json_history(Path.home() / ".rhodium" / "history.json")
    return _shared_db
