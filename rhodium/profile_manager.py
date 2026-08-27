"""Central persistent QWebEngineProfile management for Rhodium.

This module owns the single persistent :class:`QWebEngineProfile` that every
normal browser tab/view uses.  It is created once, configured for on-disk
persistence (cookies, HTTP cache, local storage, IndexedDB, service workers,
etc.), and kept alive for the lifetime of the application.

Storage lives in an OS-appropriate writable location (via ``QStandardPaths``),
never inside the source tree, and the location is centralized/overridable.
"""

import logging
import os
from pathlib import Path

from PyQt6.QtCore import QObject, QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile

logger = logging.getLogger("rhodium.profile")


class ProfileManager(QObject):
    """Owns the one persistent ``QWebEngineProfile`` used by all Rhodium tabs.

    The profile is created lazily on first access and cached.  If the requested
    storage location cannot be prepared, it transparently falls back to the
    built-in default (still persistent) profile so the browser keeps working.
    """

    #: Override to relocate the whole profile tree (used by tests/config).
    BASE_DIR = None

    def __init__(self, parent: QObject = None, base_dir=None):
        super().__init__(parent)
        self._base_dir = self._resolve_base_dir(base_dir)
        self._profile: QWebEngineProfile = None

    # ── Path resolution ─────────────────────────────────────────────────────
    @staticmethod
    def _resolve_base_dir(base_dir):
        if base_dir:
            return Path(base_dir)
        if ProfileManager.BASE_DIR:
            return Path(ProfileManager.BASE_DIR)
        # OS-appropriate, non-source writable location:
        #   Windows : %LOCALAPPDATA%/Rhodium
        #   macOS   : ~/Library/Application Support/Rhodium
        #   Linux   : ~/.local/share/Rhodium
        for loc in (
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation),
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation),
        ):
            if loc:
                return Path(loc) / "Rhodium"
        # Final fallback (should rarely be needed).
        return Path(os.path.expanduser("~")) / ".rhodium" / "Rhodium"

    def base_dir(self) -> Path:
        return self._base_dir

    def storage_dir(self) -> Path:
        """Persistent site data (cookies, localStorage, IndexedDB, SW, …)."""
        return self._base_dir / "WebProfile"

    def cache_dir(self) -> Path:
        """Persistent HTTP cache."""
        return self._base_dir / "WebCache"

    # ── Profile access ──────────────────────────────────────────────────────
    def profile(self) -> QWebEngineProfile:
        if self._profile is not None:
            return self._profile

        storage = self.storage_dir()
        cache = self.cache_dir()
        try:
            storage.mkdir(parents=True, exist_ok=True)
            cache.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            logger.warning(
                "Rhodium: cannot prepare profile storage at %s (%s); "
                "falling back to the default profile.", storage, exc)
            self._profile = QWebEngineProfile.defaultProfile()
            return self._profile

        try:
            # A *named* profile is persistent; an unnamed one would be
            # off-the-record (in-memory only).  Parenting it to this manager
            # keeps it alive for the whole application lifetime.
            prof = QWebEngineProfile("Rhodium", self)
            prof.setPersistentStoragePath(str(storage))
            prof.setCachePath(str(cache))
            prof.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            # Generous but bounded disk cache.
            prof.setHttpCacheMaximumSize(300 * 1024 * 1024)
            # Persist cookies on disk (respecting each site's cookie expiry,
            # i.e. logins survive restart only where the site permits).
            prof.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
            )
            self._profile = prof
            logger.info("Rhodium: persistent profile at %s", storage)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception(
                "Rhodium: failed to create persistent profile (%s); "
                "falling back to the default profile.", exc)
            self._profile = QWebEngineProfile.defaultProfile()

        return self._profile


_manager: ProfileManager = None


def get_profile_manager() -> ProfileManager:
    """Return the process-wide :class:`ProfileManager` singleton."""
    global _manager
    if _manager is None:
        _manager = ProfileManager()
    return _manager


def get_web_profile() -> QWebEngineProfile:
    """Return the single persistent ``QWebEngineProfile`` for normal browsing."""
    return get_profile_manager().profile()
