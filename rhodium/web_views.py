import urllib.parse
from PyQt6.QtCore import Qt, QUrl, QPoint, QTimer, QEvent, QElapsedTimer, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from rhodium.profile_manager import get_web_profile

from rhodium.utils import ICONS_DIR

# ── Middle-button autoscroll tuning ──────────────────────────────────────────
AUTOSCROLL_ICON_PATH = ICONS_DIR / "scroll.png"
AUTOSCROLL_DEAD_ZONE = 6        # px around the anchor where no scrolling happens
AUTOSCROLL_SPEED = 0.15         # scroll px per frame, per px of offset from anchor
AUTOSCROLL_TICK_MS = 16         # ~60 fps scroll updates

class RhodiumWebEnginePage(QWebEnginePage):
    def __init__(self, browser_window, view=None, parent=None, profile=None):
        if profile is None:
            profile = get_web_profile()
        super().__init__(profile, parent)
        self.browser_window = browser_window
        self._view = view if view is not None else parent

    def view(self):
        return self._view

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        url_str = url.toString()
        if url_str.startswith("rhodium://suggest?query="):
            query = urllib.parse.unquote(url_str.split("rhodium://suggest?query=")[1])
            if self._view is not None:
                self.browser_window.show_home_suggestions(query, self._view)
            return False
        elif url_str.startswith("rhodium://suggest-key?key="):
            key = urllib.parse.unquote(url_str.split("rhodium://suggest-key?key=")[1])
            if self._view is not None:
                self.browser_window.handle_home_suggest_key(key, self._view)
            return False
        elif url_str == "rhodium://suggest-hide":
            self.browser_window.hide_home_popup()
            return False
        if url_str.startswith("rhodium://navigate?q="):
            query = url_str.split("rhodium://navigate?q=")[1]
            decoded_query = urllib.parse.unquote(query)
            decoded_query = self.browser_window.resolve_home_search(decoded_query)
            self.browser_window.load_url(decoded_query)
            return False
        elif url_str.startswith("rhodium://retry?url="):
            target_url = url_str.split("rhodium://retry?url=")[1]
            decoded_url = urllib.parse.unquote(target_url)
            # Find the view associated with this page and reload/load the original URL
            if self._view is not None:
                self._view.setUrl(QUrl(decoded_url))
            return False
        elif url_str.startswith("rhodium://download-action?"):
            params = urllib.parse.parse_qs(url.query())
            download_id = int(params.get("id", ["-1"])[0])
            action = params.get("action", [""])[0]
            self.browser_window.handle_download_action(download_id, action)
            return False
        elif url_str.startswith("rhodium://downloads-clear"):
            self.browser_window.clear_download_history()
            return False
        elif url_str.startswith("rhodium://history-action?"):
            params = urllib.parse.parse_qs(url.query())
            action = params.get("action", [""])[0]
            target_url = params.get("url", [""])[0]
            self.browser_window.handle_history_action(target_url, action)
            return False
        elif url_str.startswith("rhodium://history-clear"):
            params = urllib.parse.parse_qs(url.query())
            range_key = params.get("range", ["all"])[0]
            self.browser_window.handle_history_clear(range_key)
            return False
        elif url_str.split("?")[0] == "rhodium://history":
            if self._view is not None:
                self.browser_window.show_history_in_view(self._view)
            return False
        elif url_str.split("?")[0] == "rhodium://downloads":
            if self._view is not None:
                self.browser_window.show_downloads_in_view(self._view)
            return False
        elif url_str.split("?")[0] == "rhodium://cookie-debugger":
            if self._view is not None:
                # Re-render uses live CookieManager data (async); avoid creating any new profile.
                self.browser_window.show_cookie_debugger_in_view(self._view)
            return False
        elif url_str.startswith("rhodium://cookie-debugger-refresh"):
            if self._view is not None:
                self.browser_window.show_cookie_debugger_in_view(self._view)
            return False
        elif url_str.startswith("rhodium://cookie-debugger-delete-all"):
            self.browser_window.handle_cookie_debugger_delete_all()
            return False
        elif url_str.startswith("rhodium://cookie-debugger-delete-domain"):
            params = urllib.parse.parse_qs(url.query())
            domain = params.get("domain", [""])[0]
            self.browser_window.handle_cookie_debugger_delete_domain(domain)
            return False
        elif url_str.startswith("rhodium://cookie-debugger-delete?"):
            params = urllib.parse.parse_qs(url.query())
            name = params.get("name", [""])[0]
            domain = params.get("domain", [""])[0]
            path = params.get("path", [""])[0]
            self.browser_window.handle_cookie_debugger_delete(name, domain, path)
            return False
        elif url_str.startswith("rhodium://cookie-debugger-set-test"):
            params = urllib.parse.parse_qs(url.query())
            name = params.get("name", ["rhodium_test"])[0]
            value = params.get("value", ["hello"])[0]
            domain = params.get("domain", [""])[0]
            self.browser_window.handle_cookie_debugger_set_test(name, value, domain)
            return False
        elif url_str.startswith("rhodium://add-shortcut"):
            self.browser_window.add_shortcut_dialog()
            return False
        elif url_str.startswith("rhodium://edit-shortcut?url="):
            target_url = url_str.split("rhodium://edit-shortcut?url=")[1]
            decoded_url = urllib.parse.unquote(target_url)
            self.browser_window.edit_shortcut_dialog(decoded_url)
            return False
        elif url_str.startswith("rhodium://delete-shortcut?url="):
            target_url = url_str.split("rhodium://delete-shortcut?url=")[1]
            decoded_url = urllib.parse.unquote(target_url)
            self.browser_window.delete_shortcut(decoded_url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, window_type):
        """Fallback for open-in-new-window requests (legacy path).

        Modern new-window requests are handled via the ``newWindowRequested``
        signal connected in ``AdvancedBrowser.add_new_tab``.  This method is
        kept so explicit "Open Link in New Window" style actions still resolve
        to a real Rhodium tab/window instead of being dropped.
        """
        from PyQt6.QtWebEngineCore import QWebEnginePage as WEP
        browser = self.browser_window
        if browser is None:
            return None
        if window_type in (WEP.WebWindowType.WebBrowserWindow,
                           WEP.WebWindowType.WebDialog):
            win = browser.open_new_window()
            view = win.get_current_view() if win is not None else None
            return view.page() if view is not None else None
        # WebBrowserTab / WebBrowserBackgroundTab -> new tab in this window
        activate = (window_type == WEP.WebWindowType.WebBrowserTab)
        view = browser.add_new_tab(activate=activate)
        return view.page() if view is not None else None


class SmoothWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scroll_target = 0
        self._scroll_animation = None
        self._pending_scroll = 0

        # Middle-button autoscroll state
        self._web_input_proxy = None
        self._autoscroll_active = False
        self._autoscroll_origin = QPoint()
        self._autoscroll_speed_x = 0.0
        self._autoscroll_speed_y = 0.0
        self._autoscroll_accum_x = 0.0
        self._autoscroll_accum_y = 0.0

        self._autoscroll_timer = QTimer(self)
        self._autoscroll_timer.setInterval(AUTOSCROLL_TICK_MS)
        self._autoscroll_timer.timeout.connect(self._tick_autoscroll)

        # Link-under-cursor cache used for middle-click / Ctrl+click handling.
        # Populated by a lightweight JavaScript hit-test on mouse move so that
        # the decision can be made synchronously when a button is pressed.
        self._hover_link = ""
        self._hover_throttle = QElapsedTimer()
        self._hover_throttle.start()
        self._consume_click = False

    # ── Middle-button autoscroll ─────────────────────────────────────────────
    def showEvent(self, event):
        self._hook_web_input()
        super().showEvent(event)

    def hideEvent(self, event):
        if self._autoscroll_active:
            self._stop_autoscroll()
        super().hideEvent(event)

    def _hook_web_input(self):
        # QtWebEngine delivers mouse input to its internal render widget
        # (focusProxy), not to the QWebEngineView itself, so we filter there.
        proxy = self.focusProxy()
        if proxy is not None and proxy is not self._web_input_proxy:
            if self._web_input_proxy is not None:
                self._web_input_proxy.removeEventFilter(self)
            proxy.installEventFilter(self)
            self._web_input_proxy = proxy

    def eventFilter(self, obj, event):
        if obj is not self._web_input_proxy:
            return super().eventFilter(obj, event)

        self._hook_web_input()
        event_type = event.type()

        # Swallow the click that opened a link in a new tab so the page does
        # not also navigate / autoscroll for that same press.
        if event_type == QEvent.Type.MouseButtonRelease and self._consume_click:
            self._consume_click = False
            return True

        # Autoscroll has priority while it is active.
        if self._autoscroll_active:
            if event_type == QEvent.Type.MouseMove:
                self._update_autoscroll_speed(event.position().toPoint())
                return True
            if (event_type == QEvent.Type.MouseButtonRelease
                    and event.button() == Qt.MouseButton.MiddleButton):
                self._stop_autoscroll()
                return True
            return super().eventFilter(obj, event)

        if event_type == QEvent.Type.MouseButtonPress:
            btn = event.button()
            mods = event.modifiers()
            if btn == Qt.MouseButton.MiddleButton:
                # Middle-click on a link opens it in a new (activated) tab and
                # must NOT start autoscroll for that link.
                if self._hover_link:
                    self._open_hover_link_new_tab()
                    self._consume_click = True
                    return True
                self._start_autoscroll(event.position().toPoint())
                return True
            if (btn == Qt.MouseButton.LeftButton
                    and mods & Qt.KeyboardModifier.ControlModifier):
                # Ctrl+left-click on a link opens it in a new (activated) tab.
                if self._hover_link:
                    self._open_hover_link_new_tab()
                    self._consume_click = True
                    return True
        elif event_type == QEvent.Type.MouseMove:
            self._update_hover_link(event.position().toPoint())

        return super().eventFilter(obj, event)

    # ── Link hit-testing (for middle / ctrl click) ───────────────────────────
    @staticmethod
    def _hit_test_script(x, y):
        return (
            "(function(x, y){"
            "  var e = document.elementFromPoint(x, y);"
            "  while (e && e.nodeType === 1 && !(e.tagName === 'A' && e.href)) {"
            "    e = e.parentElement;"
            "  }"
            "  if (e && e.tagName === 'A' && e.href) { return e.href; }"
            "  return '';"
            "})(%d, %d)" % (int(x), int(y))
        )

    def _update_hover_link(self, pos):
        # Throttle the JavaScript hit-test so we are not spamming the renderer
        # on every single mouse-move pixel.
        if not self._hover_throttle.hasExpired(25):
            return
        self._hover_throttle.start()
        page = self.page()
        if page is None:
            return
        page.runJavaScript(self._hit_test_script(pos.x(), pos.y()),
                           self._on_hit_test_result)

    def _on_hit_test_result(self, href):
        self._hover_link = href if isinstance(href, str) and href else ""

    def _open_hover_link_new_tab(self):
        href = self._hover_link
        if not href:
            return
        self._hover_link = ""
        browser = getattr(self, "rhodium_browser", None)
        if browser is not None:
            browser.open_link_new_tab(href, activate=True)

    def _clear_hover_link(self):
        self._hover_link = ""

    def _start_autoscroll(self, pos):
        self._autoscroll_active = True
        self._autoscroll_origin = pos
        self._autoscroll_speed_x = 0.0
        self._autoscroll_speed_y = 0.0
        self._autoscroll_accum_x = 0.0
        self._autoscroll_accum_y = 0.0
        self._update_autoscroll_speed(pos)
        self._set_autoscroll_cursor()
        self._autoscroll_timer.start()

    def _update_autoscroll_speed(self, pos):
        dx = pos.x() - self._autoscroll_origin.x()
        dy = pos.y() - self._autoscroll_origin.y()
        self._autoscroll_speed_x = self._axis_scroll_speed(dx)
        self._autoscroll_speed_y = self._axis_scroll_speed(dy)

    @staticmethod
    def _axis_scroll_speed(delta):
        distance = abs(delta)
        if distance <= AUTOSCROLL_DEAD_ZONE:
            return 0.0
        speed = (distance - AUTOSCROLL_DEAD_ZONE) * AUTOSCROLL_SPEED
        return speed if delta > 0 else -speed

    def _tick_autoscroll(self):
        self._autoscroll_accum_x += self._autoscroll_speed_x
        self._autoscroll_accum_y += self._autoscroll_speed_y

        step_x = int(self._autoscroll_accum_x)
        step_y = int(self._autoscroll_accum_y)
        if step_x == 0 and step_y == 0:
            return

        self._autoscroll_accum_x -= step_x
        self._autoscroll_accum_y -= step_y
        self.page().runJavaScript(f"window.scrollBy({step_x}, {step_y});")

    def _stop_autoscroll(self):
        self._autoscroll_active = False
        self._autoscroll_timer.stop()
        self._autoscroll_speed_x = 0.0
        self._autoscroll_speed_y = 0.0
        self._autoscroll_accum_x = 0.0
        self._autoscroll_accum_y = 0.0
        self.unsetCursor()

    def _set_autoscroll_cursor(self):
        pixmap = QPixmap(str(AUTOSCROLL_ICON_PATH))
        if pixmap.isNull():
            self.setCursor(Qt.CursorShape.BlankCursor)
            return
        if max(pixmap.width(), pixmap.height()) > 32:
            pixmap = pixmap.scaled(
                32, 32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        hotspot = QPoint(pixmap.width() // 2, pixmap.height() // 2)
        self.setCursor(QCursor(pixmap, hotspot.x(), hotspot.y()))

    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        if delta == 0:
            return

        # Chromium normally scrolls around 40-120 px per wheel step.
        # We increase it slightly for a browser-like feel.
        scroll_amount = int(delta * 1.5)


        # Store the requested movement.
        self._pending_scroll = scroll_amount

        event.accept()

    