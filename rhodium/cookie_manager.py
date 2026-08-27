"""Cookie management for Rhodium.

This wraps the cookie store of the single persistent ``QWebEngineProfile``
used by all normal tabs.  QtWebEngine/Chromium remains the authoritative store
for cookie security and persistence (secure, HttpOnly, domain/path, session vs
persistent, expiry).  This module only *observes* the store and exposes clean
backend helpers (list / delete) for later UI work in Phase 5.

No second copy of cookies is persisted to SQLite/JSON — the in-memory index
below is purely a convenience view kept in sync from the store's own signals.
"""

from PyQt6.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWebEngineCore import QWebEngineCookieStore

from rhodium.profile_manager import get_web_profile, get_profile_manager

Qt_ISO = Qt.DateFormat.ISODate


def _cookie_key(cookie: QNetworkCookie):
    """(name, domain, path) uniquely identifies a cookie in the store."""
    return (
        bytes(cookie.name()).decode("utf-8", "replace"),
        cookie.domain(),
        cookie.path(),
    )


def _domain_matches(cookie_domain: str, target: str) -> bool:
    """True if ``cookie_domain`` belongs to ``target`` (sub-domain aware).

    Cookie domains are stored with a leading dot (e.g. ``.example.com``);
    host domains are not.  A cookie for ``.example.com`` matches a request to
    delete/query ``example.com`` as well as ``sub.example.com``.
    """
    cd = cookie_domain.lower().lstrip(".")
    t = target.lower().lstrip(".")
    if not cd or not t:
        return False
    return t == cd or t.endswith("." + cd)


class CookieManager(QObject):
    """Thin, signal-aware wrapper around ``QWebEngineProfile.cookieStore``."""

    # Re-emitted when the underlying store gains/removes a cookie (after the
    # initial bulk load).  An "update" surfaces as a removed+added pair.
    cookieAdded = pyqtSignal(QNetworkCookie)
    cookieRemoved = pyqtSignal(QNetworkCookie)

    def __init__(self, profile=None, parent: QObject = None):
        super().__init__(parent)
        if profile is None:
            profile = get_web_profile()
        self._store: QWebEngineCookieStore = profile.cookieStore()

        # Light in-memory view (NOT persisted anywhere).
        self._cookies = {}

        self._emit_changes = False
        self._store.cookieAdded.connect(self._on_cookie_added)
        self._store.cookieRemoved.connect(self._on_cookie_removed)

        # Bulk-load existing cookies into the view without spamming listeners
        # with "added" events for cookies that were already there at startup.
        self._store.loadAllCookies()
        QTimer.singleShot(400, lambda: setattr(self, "_emit_changes", True))

    # ── Signal handlers ──────────────────────────────────────────────────────
    def _on_cookie_added(self, cookie: QNetworkCookie):
        self._cookies[_cookie_key(cookie)] = cookie
        if self._emit_changes:
            self.cookieAdded.emit(cookie)

    def _on_cookie_removed(self, cookie: QNetworkCookie):
        self._cookies.pop(_cookie_key(cookie), None)
        if self._emit_changes:
            self.cookieRemoved.emit(cookie)

    # ── Access ──────────────────────────────────────────────────────────────
    def store(self) -> QWebEngineCookieStore:
        return self._store

    def list_cookies(self):
        """Return all known cookies as ``QNetworkCookie`` objects."""
        return list(self._cookies.values())

    def list_cookies_for_domain(self, domain: str):
        """Return cookies whose domain matches ``domain`` (sub-domain aware)."""
        return [c for c in self._cookies.values()
                if _domain_matches(c.domain(), domain)]

    def get_cookie(self, name: str, domain: str, path: str = "/"):
        """Return the cookie matching name/domain/path, or ``None``."""
        return self._cookies.get((name, domain, path))

    # ── Deletion ─────────────────────────────────────────────────────────────
    def delete_cookie(self, name: str, domain: str, path: str = "/") -> bool:
        """Delete a single cookie identified by name/domain/path."""
        cookie = self._cookies.get((name, domain, path))
        if cookie is None:
            return False
        self._store.deleteCookie(cookie)  # cookieRemoved updates the view
        return True

    def delete_cookies_for_domain(self, domain: str) -> int:
        """Delete every cookie whose domain matches ``domain``. Returns count."""
        targets = self.list_cookies_for_domain(domain)
        for cookie in targets:
            self._store.deleteCookie(cookie)
        return len(targets)

    def delete_all_cookies(self):
        """Delete every cookie in the store."""
        self._store.deleteAllCookies()

    def delete_session_cookies(self):
        """Delete only session cookies (those without an expiry)."""
        self._store.deleteSessionCookies()

    # ── Serialization helper (not persisted) ────────────────────────────────
    @staticmethod
    def as_dict(cookie: QNetworkCookie) -> dict:
        """Convert a cookie to a plain dict for UI consumption (no storage)."""
        expiry = cookie.expirationDate()
        return {
            "name": bytes(cookie.name()).decode("utf-8", "replace"),
            "value": bytes(cookie.value()).decode("utf-8", "replace"),
            "domain": cookie.domain(),
            "path": cookie.path(),
            "secure": cookie.isSecure(),
            "httpOnly": cookie.isHttpOnly(),
            "session": cookie.isSessionCookie(),
            "expires": expiry.toString(Qt_ISO) if (expiry and expiry.isValid()) else None,
            "sameSite": cookie.sameSitePolicy().name
            if hasattr(cookie.sameSitePolicy(), "name") else str(cookie.sameSitePolicy()),
        }


_manager: CookieManager = None


def get_cookie_manager() -> CookieManager:
    """Return the process-wide :class:`CookieManager` for the persistent profile."""
    global _manager
    if _manager is None:
        _manager = CookieManager(parent=get_profile_manager())
    return _manager
