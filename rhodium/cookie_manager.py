"""Cookie manager for Rhodium browser.

Manages cookies using QtWebEngine's persistent QWebEngineCookieStore.
All browser tabs share the same cookie store via the persistent QWebEngineProfile.

Key Points:
- Does NOT create or store cookies; Chromium handles that
- All WebView tabs must use the same QWebEngineProfile for shared cookies
- Cookie operations are async (QtWebEngine has no sync cookie API)
- Signal availability depends on Qt version (graceful fallback)
"""

import logging
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtWebEngineCore import QWebEngineProfile
from rhodium.profile_manager import get_web_profile

logger = logging.getLogger("Rhodium.CookieManager")


class CookieManager(QObject):
    """
    Manages cookies using QtWebEngine's persistent QWebEngineCookieStore.

    Key Points:
    - Does NOT create or store cookies; Chromium handles that
    - All WebView tabs must use the same QWebEngineProfile for shared cookies
    - Cookie operations are async (QtWebEngine has no sync cookie API)
    - Signal availability depends on Qt version (graceful fallback)
    """

    # Signals - emitted when cookie operations complete
    cookie_added = pyqtSignal(object)          # Emitted when cookie added
    cookie_removed = pyqtSignal(object)        # Emitted when cookie removed
    cookies_cleared = pyqtSignal()             # Emitted when all cookies deleted
    cookies_updated = pyqtSignal()             # Emitted on any cookie change

    def __init__(self, profile: QWebEngineProfile = None):
        """
        Initialize CookieManager with a QWebEngineProfile.

        If profile is None, it will be fetched from the persistent profile manager.

        Args:
            profile: The QWebEngineProfile from Rhodium (defaults to the persistent profile)

        Raises:
            ValueError: If profile is None or cookieStore() returns None
        """
        super().__init__()

        if profile is None:
            profile = get_web_profile()

        if profile is None:
            raise ValueError("CookieManager requires non-None QWebEngineProfile")

        self.profile = profile
        self.cookie_store = profile.cookieStore()

        if self.cookie_store is None:
            raise ValueError("QWebEngineProfile.cookieStore() returned None")

        logger.info(f"CookieManager initialized")
        logger.info(f"Storage path: {profile.persistentStoragePath()}")

        # In-memory cache of live cookies (both persistent and session).
        # QtWebEngine's loadAllCookies only re-emits persistent cookies, so
        # we keep a live cache via cookieAdded/cookieRemoved signals.
        self._cookie_cache: dict = {}
        self._cache_loaded = False

        self._connect_cookie_signals()
        # Populate cache with persistent cookies on startup
        try:
            self.cookie_store.loadAllCookies()
            self._cache_loaded = True
        except Exception as e:
            logger.debug(f"Initial loadAllCookies failed: {e}")

    # ------------------------------------------------------------------
    # Signal connection with graceful fallback
    # ------------------------------------------------------------------

    def _connect_cookie_signals(self):
        """Connect to QWebEngineCookieStore signals with graceful fallback."""

        try:
            if hasattr(self.cookie_store, 'cookieAdded'):
                self.cookie_store.cookieAdded.connect(self._on_cookie_added)
                logger.info("Connected to cookieAdded signal")
            else:
                logger.debug("cookieAdded signal not available")
        except Exception as e:
            logger.debug(f"Could not connect cookieAdded: {e}")

        try:
            if hasattr(self.cookie_store, 'cookieRemoved'):
                self.cookie_store.cookieRemoved.connect(self._on_cookie_removed)
                logger.info("Connected to cookieRemoved signal")
            else:
                logger.debug("cookieRemoved signal not available")
        except Exception as e:
            logger.debug(f"Could not connect cookieRemoved: {e}")

        try:
            if hasattr(self.cookie_store, 'cookieChanged'):
                self.cookie_store.cookieChanged.connect(self._on_cookie_changed)
                logger.info("Connected to cookieChanged signal")
            else:
                logger.debug("cookieChanged signal not available")
        except Exception as e:
            logger.debug(f"Could not connect cookieChanged: {e}")

    # ------------------------------------------------------------------
    # Internal signal handlers
    # ------------------------------------------------------------------

    def _cookie_key(self, cookie):
        try:
            name = cookie.name()
            name = name.data().decode() if hasattr(name, "data") else (name.decode() if isinstance(name, bytes) else str(name))
        except Exception:
            name = ""
        try:
            domain = cookie.domain() or ""
        except Exception:
            domain = ""
        try:
            path = cookie.path() or "/"
        except Exception:
            path = "/"
        return (name, domain, path)

    def _on_cookie_added(self, cookie):
        """Internal: called when cookie added."""
        try:
            from PyQt6.QtNetwork import QNetworkCookie
            # Copy the cookie - the signal argument is a temporary reference
            # that will be destroyed after the slot returns. Storing it directly
            # would leave a dangling wrapper with empty data and could crash
            # Chromium when later accessed.
            copy = QNetworkCookie(cookie)
            self._cookie_cache[self._cookie_key(copy)] = copy
        except Exception:
            try:
                self._cookie_cache[self._cookie_key(cookie)] = cookie
            except Exception:
                pass
        logger.debug(f"Cookie added: {self._cookie_to_string(cookie)}")
        self.cookie_added.emit(cookie)
        self.cookies_updated.emit()

    def _on_cookie_removed(self, cookie):
        """Internal: called when cookie removed."""
        try:
            self._cookie_cache.pop(self._cookie_key(cookie), None)
        except Exception:
            pass
        logger.debug(f"Cookie removed: {self._cookie_to_string(cookie)}")
        self.cookie_removed.emit(cookie)
        self.cookies_updated.emit()

    def _on_cookie_changed(self, cookie, removed):
        """Internal: called when cookie changed."""
        action = "removed" if removed else "added"
        logger.debug(f"Cookie {action}: {self._cookie_to_string(cookie)}")
        try:
            if removed:
                self._cookie_cache.pop(self._cookie_key(cookie), None)
                self.cookie_removed.emit(cookie)
            else:
                from PyQt6.QtNetwork import QNetworkCookie
                copy = QNetworkCookie(cookie)
                self._cookie_cache[self._cookie_key(copy)] = copy
                self.cookie_added.emit(cookie)
        except Exception:
            if removed:
                self.cookie_removed.emit(cookie)
            else:
                self.cookie_added.emit(cookie)
        self.cookies_updated.emit()

    @staticmethod
    def _cookie_to_string(cookie) -> str:
        """Convert cookie to readable string for logging."""
        try:
            name = cookie.name().decode() if isinstance(cookie.name(), bytes) else cookie.name()
            return f"{name} (domain={cookie.domain()}, path={cookie.path()})"
        except Exception:
            return str(cookie)

    # ------------------------------------------------------------------
    # PUBLIC API: COOKIE OPERATIONS
    # ------------------------------------------------------------------

    def get_all_cookies_async(self, callback):
        """
        Get all cookies asynchronously.

        IMPORTANT: QtWebEngine provides NO synchronous cookie API.
        Cookies are collected via ``loadAllCookies`` which re-emits
        ``cookieAdded`` for every stored cookie.

        Args:
            callback: Function(cookies_list) called when ready
                     cookies_list is list of QNetworkCookie objects
        """
        try:
            # If the Qt build exposes a direct getAllCookies style API, try it.
            if hasattr(self.cookie_store, "getAllCookies"):
                self.cookie_store.getAllCookies(callback)  # type: ignore[attr-defined]
                return
            if hasattr(self.cookie_store, "getCookies"):
                self.cookie_store.getCookies(callback)  # type: ignore[attr-defined]
                return
        except Exception as e:
            logger.debug(f"Direct getCookies not available: {e}")

        # Fallback: live cache (session + persistent) populated via signals.
        # loadAllCookies re-emits persistent cookies; session cookies are already
        # in the cache from earlier cookieAdded events (including setCookie).
        try:
            from PyQt6.QtCore import QTimer
            try:
                # Refresh persistent store — new persistent cookies will flow via signal
                self.cookie_store.loadAllCookies()
            except Exception as e:
                logger.debug(f"loadAllCookies failed: {e}")

            def deliver():
                # Return a snapshot of the live cache
                callback(list(self._cookie_cache.values()))

            # Small delay so loadAllCookies signals have time to repopulate
            QTimer.singleShot(350, deliver)
        except Exception as e:
            logger.warning(f"get_all_cookies_async fallback failed: {e}")
            callback([])

    def delete_cookie(self, cookie_name: str, domain: str = None) -> bool:
        """
        Delete a specific cookie by name and optional domain.

        Args:
            cookie_name: Name of cookie to delete
            domain: Optional domain to filter (if None, delete from any domain)

        Returns:
            bool: True if operation initiated

        Example:
            manager.delete_cookie("sessionid", "example.com")
        """
        try:
            def delete_if_matches(cookies):
                for cookie in cookies:
                    cookie_name_str = cookie.name().decode() if isinstance(cookie.name(), bytes) else cookie.name()
                    if cookie_name_str == cookie_name:
                        if domain is None or cookie.domain() == domain:
                            if self.cookie_store.deleteCookie(cookie):
                                logger.info(f"Deleted: {cookie_name} (domain={cookie.domain()})")

            self.get_all_cookies_async(delete_if_matches)
            return True
        except Exception as e:
            logger.error(f"Error deleting cookie {cookie_name}: {e}")
            return False

    def delete_cookies_for_domain(self, domain: str) -> int:
        """
        Delete all cookies for a specific domain.

        Args:
            domain: Domain to clear (e.g., "facebook.com")

        Returns:
            int: Approximate number of cookies deleted

        Example:
            manager.delete_cookies_for_domain("facebook.com")
        """
        deleted_count = [0]

        try:
            def delete_domain_cookies(cookies):
                for cookie in cookies:
                    if domain.lower() in cookie.domain().lower() or \
                       cookie.domain().lower() in domain.lower():
                        if self.cookie_store.deleteCookie(cookie):
                            deleted_count[0] += 1
                            logger.info(f"Deleted: {cookie.name()} from {cookie.domain()}")

            self.get_all_cookies_async(delete_domain_cookies)
            return deleted_count[0]
        except Exception as e:
            logger.error(f"Error deleting domain cookies: {e}")
            return 0

    def delete_all_cookies(self) -> bool:
        """
        Delete ALL cookies from all domains.

        WARNING: This clears login sessions, saved preferences, etc.

        Returns:
            bool: True if operation initiated

        Example:
            manager.delete_all_cookies()
        """
        try:
            deleted = False
            if hasattr(self.cookie_store, 'deleteAllCookies'):
                try:
                    self.cookie_store.deleteAllCookies()
                    deleted = True
                except Exception as e:
                    logger.debug(f"deleteAllCookies failed: {e}")
            if hasattr(self.cookie_store, 'deleteSessionCookies'):
                try:
                    self.cookie_store.deleteSessionCookies()
                    deleted = True
                except Exception as e:
                    logger.debug(f"deleteSessionCookies failed: {e}")
            if deleted:
                # Clear local cache optimistically; real removal will flow via signals
                try:
                    self._cookie_cache.clear()
                except Exception:
                    pass
                logger.info("Deleted all cookies")
                self.cookies_cleared.emit()
                return True
            # Fallback: manually delete each cookie
            def delete_all(cookies):
                count = 0
                for cookie in cookies:
                    try:
                        if self.cookie_store.deleteCookie(cookie):
                            count += 1
                    except Exception:
                        pass
                logger.info(f"Deleted {count} cookies (fallback method)")
                self.cookies_cleared.emit()

            self.get_all_cookies_async(delete_all)
            return True
        except Exception as e:
            logger.error(f"Error deleting all cookies: {e}")
            return False

    def set_test_cookie(self, name: str, value: str, domain: str = "", path: str = "/", secure: bool = False, httponly: bool = False) -> bool:
        """Create a test cookie via the live QWebEngineCookieStore.

        Uses ``setCookie`` so the cookie flows through Chromium and is
        subject to normal domain/path rules.  The origin URL is derived
        from the domain when possible.
        """
        try:
            from PyQt6.QtNetwork import QNetworkCookie
            from PyQt6.QtCore import QUrl
            cookie = QNetworkCookie()
            # QNetworkCookie name/value are QByteArray
            cookie.setName(name.encode() if isinstance(name, str) else name)
            cookie.setValue(value.encode() if isinstance(value, str) else value)
            if domain:
                cookie.setDomain(domain)
            if path:
                cookie.setPath(path)
            cookie.setSecure(secure)
            cookie.setHttpOnly(httponly)
            # Session cookies have no expiration; setting an expiration makes it persistent
            # Leave expiration empty for session-style test (we want to show difference).
            origin = QUrl(f"https://{domain}" if domain else "https://example.com")
            self.cookie_store.setCookie(cookie, origin)
            logger.info(f"Set test cookie: {name} domain={domain} path={path}")
            return True
        except Exception as e:
            logger.error(f"Failed to set test cookie {name}: {e}")
            return False

    def get_cookie_count_async(self, callback):
        """
        Get total cookie count asynchronously.

        Args:
            callback: Function(count) called with total cookie count

        Example:
            manager.get_cookie_count_async(lambda n: print(f"Cookies: {n}"))
        """
        def count_cookies(cookies):
            callback(len(cookies))

        self.get_all_cookies_async(count_cookies)

    def get_storage_path(self) -> str:
        """Get the file system path where cookies are stored."""
        return self.profile.persistentStoragePath()

    def is_persistent(self) -> bool:
        """Check if cookie persistence is enabled."""
        path = self.profile.persistentStoragePath()
        return path is not None and len(path) > 0

    # ------------------------------------------------------------------
    # DEBUGGING & TESTING
    # ------------------------------------------------------------------

    def print_all_cookies_debug(self):
        """Print all cookies to log (debugging only)."""
        def print_cookies(cookies):
            logger.info(f"=== ALL COOKIES ({len(cookies)} total) ===")
            for i, cookie in enumerate(cookies, 1):
                name = cookie.name().decode() if isinstance(cookie.name(), bytes) else cookie.name()
                value = cookie.value().decode() if isinstance(cookie.value(), bytes) else cookie.value()
                logger.info(
                    f"  {i}. {name}={value[:30]}... | "
                    f"domain={cookie.domain()}, secure={cookie.isSecure()}, "
                    f"httponly={cookie.isHttpOnly()}, session={cookie.isSessionCookie()}"
                )

        self.get_all_cookies_async(print_cookies)

    def export_cookies_json_debug(self, filepath: str):
        """Export cookies to JSON file (debugging only)."""
        def export_cookies(cookies):
            import json
            from datetime import datetime
            data = {
                "exported": datetime.now().isoformat(),
                "total": len(cookies),
                "cookies": []
            }

            for cookie in cookies:
                name = cookie.name().decode() if isinstance(cookie.name(), bytes) else cookie.name()
                value = cookie.value().decode() if isinstance(cookie.value(), bytes) else cookie.value()

                data["cookies"].append({
                    "name": name,
                    "value": value,
                    "domain": cookie.domain(),
                    "path": cookie.path(),
                    "secure": cookie.isSecure(),
                    "httponly": cookie.isHttpOnly(),
                    "session": cookie.isSessionCookie(),
                })

            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Exported {len(cookies)} cookies to {filepath}")
            except Exception as e:
                logger.error(f"Export failed: {e}")

        self.get_all_cookies_async(export_cookies)