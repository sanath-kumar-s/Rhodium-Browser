"""Centralized dual-mode fullscreen controller for Rhodium.

Two logically-independent fullscreen states are managed here:

* ``browser_fullscreen`` — toggled by F11, hides the browser chrome so the
  active tab fills the screen.
* ``website_fullscreen`` — requested by web pages through the JavaScript
  Fullscreen API (``QWebEnginePage.fullScreenRequested``).

The two states are tracked separately. Either one being active keeps the
window fullscreen; the last one to clear returns the UI to the exact state
it was in before fullscreen began.
"""

from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings


class FullscreenController(QObject):
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

        # Independent state flags
        self.browser_fullscreen = False
        self.website_fullscreen = False
        self.website_page = None        # QWebEnginePage owning website fullscreen
        self.website_view = None        # QWebEngineView owning website fullscreen

        # Saved window state for exact restore
        self.previous_window_state = None
        self._saved_geometry = None
        self._saved_margins = None
        self._saved_visibility = {}
        self._applied = False          # True while chrome is actually hidden

        self._enable_fullscreen_support()
        self._install_f11_action()

        # Attach to any views that already exist.
        for view in self.browser.findChildren(QWebEngineView):
            self.attach_view(view)

        # Watch tab changes so switching away from a fullscreen tab exits it.
        tab_widget = getattr(self.browser, "tab_widget", None)
        if tab_widget is not None:
            tab_widget.currentChanged.connect(self._on_current_changed)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _enable_fullscreen_support(self):
        try:
            from rhodium.profile_manager import get_web_profile
            settings = get_web_profile().settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        except Exception:
            pass

    def _install_f11_action(self):
        self.f11_action = QAction("Toggle Browser Fullscreen", self.browser)
        self.f11_action.setShortcut(QKeySequence(Qt.Key.Key_F11))
        self.f11_action.triggered.connect(self.toggle_browser_fullscreen)
        self.browser.addAction(self.f11_action)

    def attach_view(self, view):
        """Wire website fullscreen handling to ``view`` (idempotent)."""
        if not isinstance(view, QWebEngineView):
            return
        page = view.page()
        if page is None:
            return
        if getattr(page, "_rh_fullscreen_attached", False):
            return
        page._rh_fullscreen_attached = True

        try:
            view.settings().setAttribute(
                QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
            )
        except Exception:
            pass

        page.fullScreenRequested.connect(
            lambda request, p=page: self._on_website_fullscreen_request(request, p)
        )

    # ------------------------------------------------------------------
    # Browser fullscreen (F11)
    # ------------------------------------------------------------------

    def toggle_browser_fullscreen(self):
        self.browser_fullscreen = not self.browser_fullscreen
        self._apply()

    # ------------------------------------------------------------------
    # Website fullscreen (JavaScript Fullscreen API)
    # ------------------------------------------------------------------

    def _on_website_fullscreen_request(self, request, page):
        try:
            request.accept()
        except RuntimeError:
            return

        if request.toggleOn():
            if self.website_fullscreen and self.website_page is not page:
                return
            self.website_page = page
            self.website_view = self._view_for_page(page)
            self.website_fullscreen = True
            self._apply()
        else:
            if not self.website_fullscreen:
                return
            if self.website_page is not None and self.website_page is not page:
                return
            self._exit_website_fullscreen()

    def _exit_website_fullscreen(self):
        self.website_fullscreen = False
        self.website_page = None
        self.website_view = None
        self._apply()

    def _terminate_website_fullscreen(self):
        """Exit website fullscreen without waiting for the page signal."""
        if not self.website_fullscreen:
            return
        page = self.website_page
        self.website_fullscreen = False
        self.website_page = None
        self.website_view = None
        if page is not None:
            try:
                page.runJavaScript(
                    "if (document.fullscreenElement) document.exitFullscreen();"
                )
            except RuntimeError:
                pass
        self._apply()

    # ------------------------------------------------------------------
    # Tab lifecycle integration
    # ------------------------------------------------------------------

    def _on_current_changed(self, index):
        if not self.website_fullscreen:
            return
        current = self.browser.tab_widget.widget(index)
        if current is self.website_view:
            return
        # Switching away from the fullscreen tab always exits website fullscreen.
        self._terminate_website_fullscreen()

    def on_view_closed(self, view):
        if self.website_fullscreen and self.website_view is view:
            self._terminate_website_fullscreen()

    # ------------------------------------------------------------------
    # Apply / restore window state
    # ------------------------------------------------------------------

    def _apply(self):
        want = self.browser_fullscreen or self.website_fullscreen
        if want and not self._applied:
            self._enter()
        elif not want and self._applied:
            self._exit()

    def _enter(self):
        w = self.browser
        self._applied = True

        self.previous_window_state = w.windowState()
        self._saved_geometry = w.saveGeometry()

        central = w.centralWidget()
        layout = central.layout() if central is not None else None
        self._saved_margins = layout.contentsMargins() if layout is not None else None
        if layout is not None:
            layout.setContentsMargins(0, 0, 0, 0)

        self._saved_visibility = {}
        for widget in self._chrome_widgets():
            self._saved_visibility[widget] = not widget.isHidden()
            widget.hide()

        w.showFullScreen()

        view = self._focus_view()
        if view is not None:
            view.setFocus(Qt.FocusReason.OtherFocusReason)

    def _exit(self):
        w = self.browser
        self._applied = False

        for widget, was_visible in self._saved_visibility.items():
            widget.setVisible(was_visible)
        self._saved_visibility = {}

        central = w.centralWidget()
        layout = central.layout() if central is not None else None
        if layout is not None and self._saved_margins is not None:
            layout.setContentsMargins(self._saved_margins)
        self._saved_margins = None

        state = self.previous_window_state or Qt.WindowState.WindowNoState
        if state & Qt.WindowState.WindowMaximized:
            w.showMaximized()
        else:
            if self._saved_geometry is not None:
                w.restoreGeometry(self._saved_geometry)
            w.showNormal()
        self.previous_window_state = None
        self._saved_geometry = None

        view = self._focus_view()
        if view is not None:
            view.setFocus(Qt.FocusReason.OtherFocusReason)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _chrome_widgets(self):
        w = self.browser
        items = [
            getattr(w, "toolbar", None),
            getattr(w, "find_bar", None),
        ]
        tab_widget = getattr(w, "tab_widget", None)
        if tab_widget is not None:
            chrome = getattr(tab_widget, "chrome_widget", None)
            if chrome is not None:
                items.append(chrome())
        status = w.statusBar() if hasattr(w, "statusBar") else None
        if status is not None:
            items.append(status)
        return [item for item in items if item is not None]

    def _focus_view(self):
        if self.website_view is not None and isinstance(self.website_view, QWebEngineView):
            return self.website_view
        current = getattr(self.browser, "tab_widget", None)
        current = current.currentWidget() if current is not None else None
        if isinstance(current, QWebEngineView):
            return current
        return current.findChild(QWebEngineView) if current is not None else None

    def _view_for_page(self, page):
        for view in self.browser.findChildren(QWebEngineView):
            if view.page() is page:
                return view
        return None
