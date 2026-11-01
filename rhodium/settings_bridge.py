"""QWebChannel bridge for the internal ``rhodium://settings`` page.

QtWebEngine does not surface in-page navigations to custom ``rhodium://``
schemes through ``acceptNavigationRequest`` when the document is loaded via
``setHtml()``.  The settings page therefore talks to Python over QWebChannel
instead of navigating by URL.

This object exposes a small, safe API:

* ``navigate(cat)``      — switch the active settings category.
* ``set_setting(key, value, cat)`` — persist a setting via SettingsService.
* ``route(url_str)``     — dispatch an existing ``rhodium://settings-*`` action
  URL to its handler (reused, so no action logic is duplicated).
"""

from PyQt6.QtCore import QObject, pyqtSlot


class SettingsBridge(QObject):
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

    @pyqtSlot(str)
    def navigate(self, cat):
        view = None
        try:
            view = self.browser.get_current_view()
        except Exception:
            view = None
        if view is not None:
            self.browser.show_settings_in_view(view, cat=cat)

    @pyqtSlot(str, str, str)
    def set_setting(self, key, value, cat):
        try:
            self.browser.handle_settings_set(cat, key, value)
        except Exception:
            pass

    @pyqtSlot(str)
    def route(self, url_str):
        try:
            self.browser.handle_settings_route(url_str)
        except Exception:
            pass
