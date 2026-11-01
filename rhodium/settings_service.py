"""Rhodium centralized settings service.

This module owns the single source of truth for every browser configuration
value.  All UI pages and browser components read/write through this service
instead of keeping their own copies, so a change made in any one place is
immediately visible everywhere else.

Storage is a structured JSON file (``~/.rhodium/settings.json``) merged with a
built-in defaults table, so missing/invalid/corrupt entries degrade gracefully
to sensible values.  A single ``QObject`` signal is emitted whenever a key
changes so the browser chrome can react (theme, zoom, privacy toggles, ...).
"""

import json
import logging
from pathlib import Path
from urllib.parse import quote_plus

from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger("rhodium.settings")

# ── Search engines ───────────────────────────────────────────────────────────
DEFAULT_SEARCH_ENGINES = [
    {
        "id": "google",
        "name": "Google",
        "search_url": "https://www.google.com/search?q={searchTerms}",
        "suggest_url": "https://suggestqueries.google.com/complete/search?client=firefox&q={searchTerms}",
        "keyword": "g",
    },
    {
        "id": "bing",
        "name": "Bing",
        "search_url": "https://www.bing.com/search?q={searchTerms}",
        "suggest_url": "https://api.bing.com/osjson.aspx?query={searchTerms}",
        "keyword": "b",
    },
    {
        "id": "duckduckgo",
        "name": "DuckDuckGo",
        "search_url": "https://duckduckgo.com/?q={searchTerms}",
        "suggest_url": "https://duckduckgo.com/ac/?q={searchTerms}&type=list",
        "keyword": "ddg",
    },
    {
        "id": "brave",
        "name": "Brave Search",
        "search_url": "https://search.brave.com/search?q={searchTerms}",
        "suggest_url": "https://search.brave.com/api/suggest?q={searchTerms}",
        "keyword": "br",
    },
    {
        "id": "yahoo",
        "name": "Yahoo",
        "search_url": "https://search.yahoo.com/search?p={searchTerms}",
        "suggest_url": "https://search.yahoo.com/sugg/oss?command={searchTerms}",
        "keyword": "y",
    },
    {
        "id": "ecosia",
        "name": "Ecosia",
        "search_url": "https://www.ecosia.org/search?q={searchTerms}",
        "suggest_url": "https://www.ecosia.org/autocomplete?q={searchTerms}",
        "keyword": "eco",
    },
    {
        "id": "startpage",
        "name": "Startpage",
        "search_url": "https://www.startpage.com/sp/search?query={searchTerms}",
        "suggest_url": "",
        "keyword": "sp",
    },
]

# Keys whose values are restricted to a fixed set.
_ENUM_VALIDATORS = {
    "general.theme": {"light", "dark", "system"},
    "general.startup_mode": {"new_tab", "continue"},
    "general.font_size": {"small", "medium", "large"},
    "privacy.notifications": {"allow", "ask", "block"},
    "privacy.location": {"allow", "ask", "block"},
    "privacy.camera": {"allow", "ask", "block"},
    "privacy.microphone": {"allow", "ask", "block"},
}

_DEFAULTS = {
    # General
    "general.startup_mode": "new_tab",
    "general.homepage": "about:home",
    "general.newtab_page": "about:home",
    "general.theme": "light",
    "general.language": "en",
    "general.zoom": 100,
    "general.font_size": "medium",
    # Search engine
    "search.default_engine": "google",
    "search.suggestions_enabled": True,
    "search.address_bar_suggestions": True,
    # Privacy & security — preferences QtWebEngine can/cannot enforce are
    # documented on the settings page itself.
    "privacy.do_not_track": False,
    "privacy.tracking_protection": True,
    "privacy.javascript_enabled": True,
    "privacy.local_storage_enabled": True,
    "privacy.cookies_enabled": True,
    "privacy.cache_enabled": True,
    "privacy.popups_blocked": True,
    "privacy.notifications": "ask",
    "privacy.location": "ask",
    "privacy.camera": "ask",
    "privacy.microphone": "ask",
    "privacy.safe_browsing": False,
    # Downloads
    "downloads.directory": str(Path.home() / "Downloads"),
    "downloads.ask_where": False,
    "downloads.open_downloads_page": False,
    "downloads.notify_completion": True,
    # Appearance
    "appearance.accent_color": "#6D4FD8",
    "appearance.show_home_button": True,
    "appearance.show_bookmarks_bar": False,
    "appearance.toolbar_style": "default",
    "appearance.home_background": "gradient",
    # Tabs & startup
    "tabs.restore_session": False,
    "tabs.open_background": False,
    "tabs.confirm_close_multiple": True,
}

_DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")


def _validate(key: str, value):
    """Return a validated value for ``key``, or None if invalid."""
    if key in _ENUM_VALIDATORS:
        if value in _ENUM_VALIDATORS[key]:
            return value
        return None
    if key == "general.zoom":
        try:
            v = int(value)
        except (TypeError, ValueError):
            return None
        return max(50, min(300, v))
    if key == "appearance.accent_color":
        if isinstance(value, str) and value.startswith("#") and len(value) == 7:
            return value
        return None
    if key in ("downloads.directory", "general.homepage", "general.newtab_page"):
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None
    if key.startswith("privacy.") and isinstance(value, bool):
        return value
    if key.startswith("search.") and isinstance(value, bool):
        return value
    if key.startswith("downloads.") and isinstance(value, bool):
        return value
    if key.startswith("appearance.") and isinstance(value, bool):
        return value
    if key.startswith("tabs.") and isinstance(value, bool):
        return value
    if key == "general.language":
        if isinstance(value, str) and value.strip():
            return value.strip()[:8]
        return None
    return value


def validate_search_url(template: str) -> str | None:
    """Normalize and validate a custom search URL template.

    Returns the cleaned template, or None when it is unusable (missing the
    ``{searchTerms}`` placeholder or not an absolute http(s) URL).
    """
    if not isinstance(template, str):
        return None
    t = template.strip()
    if "{searchTerms}" not in t:
        return None
    if not (t.startswith("http://") or t.startswith("https://")):
        return None
    return t


def build_search_url(template: str, query: str) -> str:
    """Substitute ``{searchTerms}`` in a template with an encoded query."""
    query = (query or "").strip()
    encoded = quote_plus(query)
    if "{searchTerms}" in template:
        return template.replace("{searchTerms}", encoded)
    # No placeholder — append query as a query parameter if possible.
    if "?" in template:
        return f"{template}&q={encoded}"
    return f"{template}?q={encoded}"


class SettingsService(QObject):
    """Single source of truth for all Rhodium configuration values.

    Attributes:
        setting_changed: pyqtSignal(str, object) emitted with the dotted key
            and its new validated value whenever a setting is updated.
        settings_reset: pyqtSignal() emitted after ``reset()``.
    """

    setting_changed = pyqtSignal(str, object)
    settings_reset = pyqtSignal()

    def __init__(self, path=None, parent=None):
        super().__init__(parent)
        self._path = Path(path) if path else Path.home() / ".rhodium" / "settings.json"
        self._data = dict(_DEFAULTS)
        # Search-engine list is stored under a dedicated key.
        self._data["search.engines"] = [dict(e) for e in DEFAULT_SEARCH_ENGINES]
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────
    def _load(self):
        try:
            if not self._path.exists():
                self._save()
                return
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("settings file is not a JSON object")
        except Exception as exc:  # missing / invalid / corrupt
            logger.warning("Rhodium settings: could not read %s (%s); using defaults",
                           self._path, exc)
            self._save()
            return

        # Merge stored values over defaults (only valid keys are kept).
        for key, value in raw.items():
            if key == "search.engines":
                cleaned = self._sanitize_engines(value)
                if cleaned:
                    self._data[key] = cleaned
                continue
            validated = _validate(key, value)
            if validated is not None and key in _DEFAULTS:
                self._data[key] = validated
        self._save()

    def _save(self):
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(self._data, indent=2), encoding="utf-8")
        except OSError as exc:
            logger.error("Could not persist settings: %s", exc)

    @staticmethod
    def _sanitize_engines(engines):
        if not isinstance(engines, list):
            return None
        out = []
        seen = set()
        for e in engines:
            if not isinstance(e, dict):
                continue
            eid = str(e.get("id", "")).strip()
            name = str(e.get("name", "")).strip()
            if not eid or not name or eid in seen:
                continue
            url = validate_search_url(e.get("search_url"))
            if not url:
                continue
            seen.add(eid)
            out.append({
                "id": eid,
                "name": name,
                "search_url": url,
                "suggest_url": str(e.get("suggest_url", "")).strip(),
                "keyword": str(e.get("keyword", "")).strip(),
            })
        return out or None

    # ── Read ─────────────────────────────────────────────────────────────────
    @property
    def data(self) -> dict:
        """Live view of the stored settings (read-only by convention)."""
        return self._data

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key]
        # Fall back to the built-in default if the stored value was dropped.
        if key in _DEFAULTS:
            return _DEFAULTS[key]
        return default

    def get_all(self) -> dict:
        return dict(self._data)

    # ── Write ────────────────────────────────────────────────────────────────
    def set(self, key, value) -> bool:
        validated = _validate(key, value)
        if validated is None:
            return False
        if key in self._data and self._data[key] == validated:
            return True
        if key.startswith("search.") and key == "search.engines":
            cleaned = self._sanitize_engines(value)
            if not cleaned:
                return False
            self._data[key] = cleaned
            self._save()
            self.setting_changed.emit(key, cleaned)
            return True
        self._data[key] = validated
        self._save()
        self.setting_changed.emit(key, validated)
        return True

    def set_many(self, mapping) -> int:
        changed = 0
        for key, value in mapping.items():
            if self.set(key, value):
                changed += 1
        return changed

    def reset(self):
        self._data = dict(_DEFAULTS)
        self._data["search.engines"] = [dict(e) for e in DEFAULT_SEARCH_ENGINES]
        self._save()
        self.settings_reset.emit()

    # ── Search engine configuration ──────────────────────────────────────────
    def engines(self) -> list:
        return [dict(e) for e in self._data.get("search.engines", [])]

    def get_engine(self, engine_id=None):
        if engine_id is None:
            engine_id = self.get("search.default_engine", "google")
        for e in self._data.get("search.engines", []):
            if e["id"] == engine_id:
                return dict(e)
        for e in DEFAULT_SEARCH_ENGINES:
            if e["id"] == engine_id:
                return dict(e)
        return dict(DEFAULT_SEARCH_ENGINES[0])

    def default_engine(self) -> dict:
        return self.get_engine(self.get("search.default_engine", "google"))

    def engine_search_url(self, engine_id=None) -> str:
        return self.get_engine(engine_id).get("search_url", "")

    def build_default_search_url(self, query: str) -> str:
        return build_search_url(self.default_engine().get("search_url", ""), query)

    def suggest_url_for(self, query: str, engine_id=None) -> str | None:
        engine = self.get_engine(engine_id)
        template = engine.get("suggest_url", "").strip()
        if not template:
            return None
        if "suggest_url" in engine and not template:
            return None
        return build_search_url(template, query)

    def set_default_engine(self, engine_id):
        if self.get_engine(engine_id).get("id"):
            self.set("search.default_engine", engine_id)

    def add_engine(self, name, search_url, suggest_url="", keyword=""):
        name = (name or "").strip()
        url = validate_search_url(search_url)
        if not name or not url:
            return None
        engines = self._data["search.engines"]
        # Find first unused id.
        used = {e["id"] for e in engines}
        n = len(engines) + 1
        while f"custom{n}" in used:
            n += 1
        engine = {
            "id": f"custom{n}",
            "name": name,
            "search_url": url,
            "suggest_url": (suggest_url or "").strip(),
            "keyword": (keyword or "").strip(),
        }
        engines.append(engine)
        self._save()
        self.setting_changed.emit("search.engines", self.engines())
        return engine

    def edit_engine(self, engine_id, name=None, search_url=None, suggest_url=None, keyword=None):
        engines = self._data["search.engines"]
        for e in engines:
            if e["id"] == engine_id:
                if name is not None:
                    name = (name or "").strip()
                    if name:
                        e["name"] = name
                if search_url is not None:
                    url = validate_search_url(search_url)
                    if not url:
                        return False
                    e["search_url"] = url
                if suggest_url is not None:
                    e["suggest_url"] = (suggest_url or "").strip()
                if keyword is not None:
                    e["keyword"] = (keyword or "").strip()
                self._save()
                self.setting_changed.emit("search.engines", self.engines())
                return True
        return False

    def delete_engine(self, engine_id):
        default_id = self.get("search.default_engine", "google")
        engines = self._data["search.engines"]
        new_engines = [e for e in engines if e["id"] != engine_id]
        if len(new_engines) == len(engines):
            return False
        self._data["search.engines"] = new_engines
        if default_id == engine_id:
            self._data["search.default_engine"] = new_engines[0]["id"]
        self._save()
        self.setting_changed.emit("search.engines", self.engines())
        if default_id == engine_id:
            self.setting_changed.emit("search.default_engine", new_engines[0]["id"])
        return True

    def restore_engines(self):
        self._data["search.engines"] = [dict(e) for e in DEFAULT_SEARCH_ENGINES]
        self._data["search.default_engine"] = "google"
        self._save()
        self.setting_changed.emit("search.engines", self.engines())
        self.setting_changed.emit("search.default_engine", "google")


_shared_service: SettingsService = None


def get_settings_service() -> SettingsService:
    """Process-wide SettingsService singleton (shared across browser windows)."""
    global _shared_service
    if _shared_service is None:
        _shared_service = SettingsService()
    return _shared_service
