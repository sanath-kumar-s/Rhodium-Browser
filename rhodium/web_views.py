import urllib.parse
from PyQt6.QtCore import QUrl, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

class RhodiumWebEnginePage(QWebEnginePage):
    def __init__(self, browser_window, view=None, parent=None):
        super().__init__(parent)
        self.browser_window = browser_window
        self._view = view if view is not None else parent

    def view(self):
        return self._view

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        url_str = url.toString()
        if url_str.startswith("rhodium://navigate?q="):
            query = url_str.split("rhodium://navigate?q=")[1]
            decoded_query = urllib.parse.unquote(query)
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
        elif url_str.split("?")[0] == "rhodium://downloads":
            if self._view is not None:
                self.browser_window.show_downloads_in_view(self._view)
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


class SmoothWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scroll_target = 0
        self._scroll_animation = None
        self._pending_scroll = 0

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

    