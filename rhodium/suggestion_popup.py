"""Browser-style suggestion popup + address bar line edit.

SuggestionPopup is a frameless, non-activating top-level frame so typing
focus never leaves the address bar / web view. It reuses a single widget
instance per owner and closes on clicks outside its bounds.

SuggestionLineEdit is a drop-in QLineEdit used for Rhodium's address bar:
it debounces text changes into SuggestionController queries and implements
browser-style keyboard navigation over the popup.
"""

from PyQt6.QtCore import Qt, QEvent, QPoint, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QVBoxLayout, QWidget,
)

from rhodium.utils import ICONS_DIR

ROW_HEIGHT = 46
MAX_VISIBLE_ROWS = 8
DEBOUNCE_MS = 180
MIN_QUERY_LEN = 2


class SuggestionPopup(QFrame):
    activated = pyqtSignal(object)   # Suggestion
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setObjectName("SuggestionPopup")

        self._suggestions = []
        self._app_filter_installed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        self.list_widget = QListWidget(self)
        self.list_widget.setObjectName("SuggestionList")
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list_widget.setMouseTracking(True)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

    # ── Public API ───────────────────────────────────────────────────────────
    def set_suggestions(self, suggestions):
        """Populate rows in place (the same popup widget is always reused)."""
        self.list_widget.clear()
        self._suggestions = list(suggestions)

        for suggestion in self._suggestions:
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(QSize(self.width() - 10, ROW_HEIGHT))
            row = self._build_row(suggestion)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, row)

        if self._suggestions:
            self.list_widget.setCurrentRow(-1)

    def suggestion_count(self):
        return len(self._suggestions)

    def show_at(self, global_pos, width):
        self.setFixedWidth(max(300, width))
        # Keep rows spanning the full popup width (hover/selection highlight).
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            hint = item.sizeHint()
            hint.setWidth(self.width() - 12)
            item.setSizeHint(hint)
        rows = min(len(self._suggestions), MAX_VISIBLE_ROWS)
        if rows == 0:
            self.hide()
            return
        height = rows * ROW_HEIGHT + 12
        self.setFixedHeight(height)
        self.move(global_pos)
        self.show()
        self.raise_()
        self._install_app_filter()

    def move_selection(self, delta):
        count = self.list_widget.count()
        if count == 0:
            return
        current = self.list_widget.currentRow()
        if current < 0:
            new_row = 0 if delta > 0 else count - 1
        else:
            new_row = (current + delta) % count
        self.list_widget.setCurrentRow(new_row)

    def selected_suggestion(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._suggestions):
            return self._suggestions[row]
        return None

    def hideEvent(self, event):
        self._remove_app_filter()
        self.closed.emit()
        super().hideEvent(event)

    # ── Internals ────────────────────────────────────────────────────────────
    def _build_row(self, suggestion):
        row = QWidget()
        row.setObjectName("SuggestionRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(9)

        icon_label = QLabel()
        icon_label.setObjectName("SuggestionIcon")
        pixmap = QPixmap(str(ICONS_DIR / suggestion.icon))
        if not pixmap.isNull():
            icon_label.setPixmap(
                pixmap.scaled(
                    16, 16,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        icon_label.setFixedSize(18, 18)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        primary = QLabel(suggestion.primary)
        primary.setObjectName("SuggestionPrimary")
        secondary = QLabel(suggestion.secondary)
        secondary.setObjectName("SuggestionSecondary")

        text_layout.addWidget(primary)
        text_layout.addWidget(secondary)
        layout.addLayout(text_layout, 1)

        return row

    def _on_item_clicked(self, item):
        row = self.list_widget.row(item)
        if 0 <= row < len(self._suggestions):
            self.list_widget.setCurrentRow(row)
            self.activated.emit(self._suggestions[row])

    # ── Close on outside click ───────────────────────────────────────────────
    def _install_app_filter(self):
        if not self._app_filter_installed:
            app = QApplication.instance()
            if app is not None:
                app.installEventFilter(self)
                self._app_filter_installed = True

    def _remove_app_filter(self):
        if self._app_filter_installed:
            app = QApplication.instance()
            if app is not None:
                app.removeEventFilter(self)
            self._app_filter_installed = False

    def eventFilter(self, obj, event):
        if (
            self.isVisible()
            and event.type() == QEvent.Type.MouseButtonPress
        ):
            try:
                global_pos = event.globalPosition().toPoint()
            except AttributeError:
                global_pos = event.globalPos()
            if not self.frameGeometry().contains(global_pos):
                self.hide()
        return False


class SuggestionLineEdit(QLineEdit):
    """Address bar line edit with debounced local suggestions."""

    suggestion_activated = pyqtSignal(object)   # Suggestion

    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = None
        self._popup = SuggestionPopup(self)
        self._suppress_suggestions = False

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(DEBOUNCE_MS)
        self._debounce.timeout.connect(self._refresh_suggestions)

        self.textChanged.connect(self._on_text_changed)
        self._popup.activated.connect(self._on_popup_activated)

    def set_controller(self, controller):
        self._controller = controller

    def suggestion_popup(self):
        return self._popup

    # ── Text changes → debounced query ───────────────────────────────────────
    def _on_text_changed(self, text):
        self._debounce.stop()
        if (
            self._suppress_suggestions
            or len(text.strip()) < MIN_QUERY_LEN
            or not self.hasFocus()
        ):
            self._popup.hide()
            return
        self._debounce.start()

    def _refresh_suggestions(self):
        if not self.hasFocus() or self._controller is None:
            return
        query = self.text().strip()
        if len(query) < MIN_QUERY_LEN:
            self._popup.hide()
            return
        suggestions = self._controller.get_address_suggestions(query, limit=MAX_VISIBLE_ROWS)
        if not suggestions:
            self._popup.hide()
            return
        self._popup.set_suggestions(suggestions)
        self._popup.show_at(self._anchor_pos(), max(320, self.width()))

    def _anchor_pos(self):
        return self.mapToGlobal(QPoint(0, self.height() + 2))

    # ── Keyboard behavior ────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        key = event.key()

        # Typing again re-enables suggestions after a navigation/selection.
        if key not in (
            Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape,
            Qt.Key.Key_Tab, Qt.Key.Key_Backtab,
            Qt.Key.Key_Shift, Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Meta,
        ):
            self._suppress_suggestions = False

        if self._popup.isVisible():
            if key == Qt.Key.Key_Down:
                self._popup.move_selection(1)
                event.accept()
                return
            if key == Qt.Key.Key_Up:
                self._popup.move_selection(-1)
                event.accept()
                return
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                suggestion = self._popup.selected_suggestion()
                self._suppress_suggestions = True
                self._debounce.stop()
                self._popup.hide()
                if suggestion is not None:
                    self.suggestion_activated.emit(suggestion)
                else:
                    super().keyPressEvent(event)   # normal navigate/search
                event.accept()
                return
            if key == Qt.Key.Key_Escape:
                self._popup.hide()
                event.accept()
                return
            if key == Qt.Key.Key_Tab:
                suggestion = self._popup.selected_suggestion()
                if suggestion is not None:
                    self._suppress_suggestions = True
                    self._debounce.stop()
                    self._popup.hide()
                    self.suggestion_activated.emit(suggestion)
                    event.accept()
                    return

        super().keyPressEvent(event)

    def _on_popup_activated(self, suggestion):
        self._suppress_suggestions = True
        self._debounce.stop()
        self._popup.hide()
        self.suggestion_activated.emit(suggestion)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        QTimer.singleShot(120, self._hide_popup_if_not_hovered)

    def _hide_popup_if_not_hovered(self):
        if self._popup.isVisible() and not self._popup.underMouse():
            self._popup.hide()
