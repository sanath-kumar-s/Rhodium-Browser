"""SuggestionController — ranked local suggestions for Rhodium.

Single source of suggestions for both the address bar and the home-page
search box. Works entirely offline from Rhodium's local SQLite data
(history + recent searches) and JSON bookmarks.
"""

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit


def normalize_url(url: str) -> str:
    """Normalize a URL for duplicate comparison only (never for navigation).

    Conservative: lowercases scheme/host, drops default ports and the
    fragment, collapses a bare root path and trailing slashes. Query strings
    are preserved so distinct pages stay distinct.
    """
    url = (url or "").strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.lower()

    scheme = parts.scheme.lower()
    host = parts.netloc.lower()
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        hostname, _, port = host.rpartition(":")
        if port in ("80", "443"):
            host = hostname

    path = parts.path
    if path == "/":
        path = ""
    else:
        while path.endswith("/"):
            path = path[:-1]

    normalized = f"{scheme}://{host}{path}"
    if parts.query:
        normalized += f"?" + parts.query
    return normalized


def display_url(url: str) -> str:
    """Shorten a URL for popup display (scheme stripped for http/https)."""
    url = (url or "").strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if parts.scheme in ("http", "https"):
        shown = parts.netloc + parts.path
        if parts.query:
            shown += "?" + parts.query
        return shown
    return url


@dataclass
class Suggestion:
    kind: str          # "url" | "search"
    primary: str       # main line shown in the popup
    secondary: str     # secondary line shown in the popup
    payload: str       # URL to load, or query text to search
    icon: str          # icon file name from style/icons


# Match tiers — higher wins (spec section 9).
_SCORE_EXACT = 100
_SCORE_PREFIX_URL = 80
_SCORE_PREFIX_TITLE = 70
_SCORE_HOST_SUBSTR = 55
_SCORE_URL_SUBSTR = 45
_SCORE_TITLE_SUBSTR = 35
_BOOKMARK_BONUS = 5


def _parse_iso(value: str):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


class SuggestionController:
    """Accepts a query, returns ranked local suggestions."""

    def __init__(self, database, bookmarks_provider=None):
        self._db = database
        self._bookmarks_provider = bookmarks_provider  # callable -> list of dicts

    # ── Public API ───────────────────────────────────────────────────────────
    def get_address_suggestions(self, query: str, limit: int = 8):
        """Suggestions for the URL/address bar (URLs + recent searches)."""
        q = (query or "").strip().lower()
        if len(q) < 2:
            return []

        entries = []          # (sort_key_tuple, Suggestion, dedupe_key)
        seen_urls = set()

        # Bookmarks are considered first so they claim their URL entry
        # (icon + ranking bonus) before plain history rows.
        for bookmark in self._get_bookmarks():
            b_url = bookmark.get("url", "")
            if not b_url:
                continue
            norm = normalize_url(b_url)
            if norm in seen_urls:
                continue
            score = self._score_url_match(q, b_url, bookmark.get("name", ""))
            if score <= 0:
                continue
            seen_urls.add(norm)
            entries.append(self._url_entry(
                {"url": b_url, "title": bookmark.get("name", ""),
                 "visit_count": 0, "last_visited": ""},
                score + _BOOKMARK_BONUS,
                icon="bookmark-filled.png",
            ))

        for row in self._db.search_urls(q):
            norm = normalize_url(row["url"])
            if norm in seen_urls:
                continue
            score = self._score_url_match(q, row["url"], row["title"])
            if score <= 0:
                continue
            seen_urls.add(norm)
            entries.append(self._url_entry(row, score, icon="history.png"))

        seen_queries = set()
        for row in self._db.search_searches(q):
            key = row["query"].strip().lower()
            if key in seen_queries:
                continue
            score = self._score_search_match(q, row["query"])
            if score <= 0:
                continue
            seen_queries.add(key)
            entries.append(self._search_entry(row, score))

        entries.sort(key=lambda e: e[0], reverse=True)
        return [entry[1] for entry in entries[:limit]]

    def get_search_suggestions(self, query: str, limit: int = 8):
        """Previous-search suggestions for the home-page search box."""
        q = (query or "").strip().lower()
        if len(q) < 2:
            return []

        entries = []
        seen = set()
        for row in self._db.search_searches(q):
            key = row["query"].strip().lower()
            if key in seen:
                continue
            score = self._score_search_match(q, row["query"])
            if score <= 0:
                continue
            seen.add(key)
            entries.append(self._search_entry(row, score))

        entries.sort(key=lambda e: e[0], reverse=True)
        return [entry[1] for entry in entries[:limit]]

    # ── Scoring ──────────────────────────────────────────────────────────────
    @staticmethod
    def _score_url_match(q: str, url: str, title: str) -> int:
        url_l = (url or "").strip().lower()
        title_l = (title or "").strip().lower()
        host_l = ""
        try:
            parts = urlsplit(url_l)
            host_l = parts.netloc.lower()
            if "@" in host_l:
                host_l = host_l.rsplit("@", 1)[-1]
            if ":" in host_l:
                host_l = host_l.rpartition(":")[0]
        except ValueError:
            pass

        score = 0
        if url_l.rstrip("/") == q or host_l == q:
            score = _SCORE_EXACT
        elif url_l.startswith(q) or host_l.startswith(q) or url_l.startswith(("http://" + q, "https://" + q)):
            score = _SCORE_PREFIX_URL
        elif title_l.startswith(q):
            score = _SCORE_PREFIX_TITLE
        elif q in host_l:
            score = _SCORE_HOST_SUBSTR
        elif q in url_l:
            score = _SCORE_URL_SUBSTR
        elif q in title_l:
            score = _SCORE_TITLE_SUBSTR
        return score

    @staticmethod
    def _score_search_match(q: str, previous: str) -> int:
        prev_l = (previous or "").strip().lower()
        if prev_l == q:
            return 100
        if prev_l.startswith(q):
            return 70
        if q in prev_l:
            return 40
        return 0

    # ── Entry builders ───────────────────────────────────────────────────────
    @staticmethod
    def _url_entry(row, score: int, icon: str):
        url = row["url"]
        title = (row.get("title") or "").strip()
        if title.lower() in ("", url.lower()):
            secondary = "Bookmark" if icon == "bookmark-filled.png" else "From history"
        else:
            secondary = title
        suggestion = Suggestion(
            kind="url",
            primary=display_url(url),
            secondary=secondary,
            payload=url,
            icon=icon,
        )
        visited = _parse_iso(row.get("last_visited") or "")
        return ((score, row.get("visit_count", 0), visited or datetime.min), suggestion, normalize_url(url))

    @staticmethod
    def _search_entry(row, score: int):
        suggestion = Suggestion(
            kind="search",
            primary=row["query"],
            secondary="Recent search",
            payload=row["query"],
            icon="search.png",
        )
        visited = _parse_iso(row.get("last_searched") or "")
        return ((score, row.get("search_count", 0), visited or datetime.min), suggestion, "search:" + row["query"].strip().lower())

    def _get_bookmarks(self):
        if self._bookmarks_provider is None:
            return []
        try:
            return self._bookmarks_provider() or []
        except Exception:
            return []
