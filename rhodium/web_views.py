import urllib.parse
from PyQt6.QtCore import QUrl, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

class RhodiumWebEnginePage(QWebEnginePage):
    def __init__(self, browser_window, parent=None):
        super().__init__(parent)
        self.browser_window = browser_window

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        url_str = url.toString()
        if url_str.startswith("rhodium://navigate?q="):
            query = url_str.split("rhodium://navigate?q=")[1]
            decoded_query = urllib.parse.unquote(query)
            self.browser_window.load_url(decoded_query)
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

        # Ask the page for its current scroll position.
        # self.page().runJavaScript(
        #     "window.scrollY",
        #     self._start_smooth_scroll
        # )

        # Store the requested movement.
        self._pending_scroll = scroll_amount

        event.accept()

    # def _start_smooth_scroll(self, current_y):
    #     if current_y is None:
    #         return

    #     current_y = float(current_y)

    #     target = current_y - self._pending_scroll

    #     # Prevent going below the top.
    #     target = max(0, target)

    #     self._scroll_target = target

    #     # Stop previous animation.
    #     if self._scroll_animation:
    #         self._scroll_animation.stop()

    #     self._scroll_animation = QPropertyAnimation(
    #         self,
    #         b"scrollPosition"
    #     )

    #     self._scroll_animation.setDuration(280)

    #     self._scroll_animation.setStartValue(current_y)
    #     self._scroll_animation.setEndValue(target)

    #     self._scroll_animation.setEasingCurve(
    #         QEasingCurve.Type.OutCubic
    #     )

    #     self._scroll_animation.start(
    #         QPropertyAnimation.DeletionPolicy.DeleteWhenStopped
    #     )

    # def get_scroll_position(self):
    #     return self._scroll_target

    # def set_scroll_position(self, value):
    #     value = float(value)

    #     self.page().runJavaScript(
    #         f"window.scrollTo(0, {value});"
    #     )

    #     self._scroll_target = value

    # scrollPosition = pyqtProperty(
    #     float,
    #     fget=get_scroll_position,
    #     fset=set_scroll_position
    # )
