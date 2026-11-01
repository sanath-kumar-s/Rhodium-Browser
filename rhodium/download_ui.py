"""Rhodium download toolbar button and popup panel.

Native PyQt interface for live download activity. The popup is a single
reusable panel anchored under the toolbar button; it opens automatically when
a download starts and can be toggled by clicking the button.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, QSize, QObject, QEvent, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QToolButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QApplication, QMenu, QWidget, QSizePolicy,
)

from rhodium.utils import icon
from rhodium.download_manager import (
    DownloadState, format_bytes, format_speed, format_eta, executable_ext,
)

BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "style" / "icons"


def type_badge(filename: str) -> QIcon:
    """Pick a file-type icon for a downloaded filename."""
    name = (filename or "").lower()
    if name.endswith((".exe", ".msi", ".msix", ".msp", ".bat", ".cmd",
                      ".ps1", ".scr", ".jar")):
        return icon("file-executable.png")
    if name.endswith((".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso")):
        return icon("file-archive.png")
    if name.endswith(".pdf"):
        return icon("file-pdf.png")
    if name.endswith((".mp3", ".wav", ".flac", ".ogg", ".m4a")):
        return icon("file-audio.png")
    if name.endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):
        return icon("file-video.png")
    if name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")):
        return icon("file-image.png")
    if name.endswith((".doc", ".docx", ".txt", ".rtf", ".odt")):
        return icon("file-document.png")
    if name.endswith((".xls", ".xlsx", ".csv", ".ods")):
        return icon("file-spreadsheet.png")
    if name.endswith((".ppt", ".pptx", ".odp")):
        return icon("file-presentation.png")
    if name.endswith((".py", ".js", ".html", ".css", ".json", ".xml", ".ts")):
        return icon("file-code.png")
    return icon("file.png")


def status_text(item) -> str:
    total = format_bytes(item.total_size)
    received = format_bytes(item.received_size)
    state = item.state
    if state == DownloadState.DOWNLOADING:
        if item.total_size > 0:
            return f"{received} / {total} · {item.percentage}%"
        return f"{received} · Downloading…"
    if state == DownloadState.PAUSED:
        return f"Paused — {received}" + (f" / {total}" if item.total_size > 0 else "")
    if state == DownloadState.COMPLETED:
        return f"Completed — {total if item.total_size > 0 else received}"
    if state == DownloadState.FAILED:
        return "Failed"
    if state == DownloadState.INTERRUPTED:
        return "Interrupted"
    if state == DownloadState.CANCELLED:
        return "Cancelled"
    return "Starting…"


class PopupDismissFilter(QObject):
    _popups = []
    _filter = None

    @classmethod
    def register(cls, popup):
        if cls._filter is None:
            cls._filter = cls(QApplication.instance())
            QApplication.instance().installEventFilter(cls._filter)
        if popup not in cls._popups:
            cls._popups.append(popup)

    @classmethod
    def unregister(cls, popup):
        if popup in cls._popups:
            cls._popups.remove(popup)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            pos = event.globalPosition().toPoint()
            for popup in list(self._popups):
                if not popup.isVisible():
                    continue
                if popup.geometry().contains(pos):
                    continue
                anchor = getattr(popup, "_anchor", None)
                if anchor is not None:
                    anchor_top_left = anchor.mapToGlobal(QPoint(0, 0))
                    if QRect(anchor_top_left, anchor.size()).contains(pos):
                        popup.close()
                        anchor._suppress_toggle = True
                        continue
                popup.close()
        return False


class DownloadMiniButton(QToolButton):
    def __init__(self, glyph, tooltip, slot, parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadMiniBtn")
        self.setText(glyph)
        self.setToolTip(tooltip)
        self.setFixedSize(26, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(slot)


class DownloadRow(QFrame):
    """A single download row used inside the popup panel."""

    def __init__(self, manager, item, panel, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.item = item
        self.panel = panel
        self.setObjectName("DownloadMenuRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(10)

        icon_label = QLabel()
        icon_label.setPixmap(type_badge(item.filename).pixmap(26, 26))
        icon_label.setObjectName("DownloadItemIcon")
        icon_label.setFixedSize(26, 26)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(icon_label)

        middle = QVBoxLayout()
        middle.setSpacing(2)

        name = QLabel(item.filename)
        name.setObjectName("DownloadItemName")
        name.setToolTip(item.filename)
        name.setMinimumWidth(0)
        name.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        middle.addWidget(name)

        self.status_label = QLabel()
        self.status_label.setObjectName("DownloadItemStatus")
        middle.addWidget(self.status_label)

        bar_wrap = QWidget()
        bar_layout = QVBoxLayout(bar_wrap)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(2)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("DownloadProgressBar")
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        bar_layout.addWidget(self.progress_bar)
        self.speed_label = QLabel()
        self.speed_label.setObjectName("DownloadItemSpeed")
        bar_layout.addWidget(self.speed_label)
        middle.addWidget(bar_wrap)

        row.addLayout(middle, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(4)
        self.btn_pause = DownloadMiniButton("⏸", "Pause", lambda: self._act("pause"), self)
        self.btn_resume = DownloadMiniButton("▶", "Resume", lambda: self._act("resume"), self)
        self.btn_cancel = DownloadMiniButton("✕", "Cancel", lambda: self._act("cancel"), self)
        self.btn_retry = DownloadMiniButton("↻", "Retry", lambda: self._act("retry"), self)
        self.btn_open = DownloadMiniButton("↗", "Open", lambda: self._act("open"), self)
        self.btn_folder = DownloadMiniButton("📂", "Show in folder", lambda: self._act("folder"), self)
        self.btn_remove = DownloadMiniButton("🗑", "Remove from list", lambda: self._act("remove"), self)

        for b in (self.btn_pause, self.btn_resume, self.btn_cancel,
                  self.btn_retry, self.btn_open, self.btn_folder, self.btn_remove):
            buttons.addWidget(b)
            b.hide()
        row.addLayout(buttons)

        self.refresh()

    def _act(self, action):
        item = self.item
        if action == "open":
            self.manager.open_file(item.id)
            self.panel.close()
        elif action == "folder":
            self.manager.show_in_folder(item.id)
        elif action == "retry":
            self.manager.retry(item.id)
        elif action == "pause":
            self.manager.pause(item.id)
        elif action == "resume":
            self.manager.resume(item.id)
        elif action == "cancel":
            self.manager.cancel(item.id)
        elif action == "remove":
            self.manager.remove(item.id)

    def refresh(self):
        item = self.item
        state = item.state

        if state == DownloadState.FAILED and item.error_message:
            self.status_label.setText("Failed — " + item.error_message[:60])
            self.status_label.setToolTip(item.error_message)
        else:
            self.status_label.setText(status_text(item))
            self.status_label.setToolTip("")

        pct = item.percentage
        if state in (DownloadState.DOWNLOADING, DownloadState.PAUSED) and pct >= 0:
            self.progress_bar.show()
            self.progress_bar.setValue(pct)
        elif state == DownloadState.COMPLETED:
            self.progress_bar.show()
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.hide()

        if state == DownloadState.DOWNLOADING:
            speed = format_speed(item.speed)
            eta = format_eta(item.eta)
            self.speed_label.setText(
                f"{speed}   ·   {eta} remaining" if speed else "Starting…")
        elif state == DownloadState.PAUSED:
            self.speed_label.setText("Paused")
        else:
            self.speed_label.setText(item.created_at.replace("T", "  "))

        self.btn_pause.setVisible(item.can_pause())
        self.btn_resume.setVisible(item.can_resume())
        self.btn_cancel.setVisible(item.is_active)
        self.btn_retry.setVisible(item.can_retry())
        self.btn_open.setVisible(state == DownloadState.COMPLETED)
        self.btn_folder.setVisible(state == DownloadState.COMPLETED)
        self.btn_remove.setVisible(state not in (DownloadState.DOWNLOADING, DownloadState.QUEUED))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.item.state == DownloadState.COMPLETED:
            self.manager.open_file(self.item.id)
            self.panel.close()
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        item = self.item
        state = item.state
        menu = QMenu(self)
        if state == DownloadState.COMPLETED:
            menu.addAction("Open", lambda: self.manager.open_file(item.id))
            menu.addAction("Open with…", lambda: self.manager.open_with(item.id))
            menu.addAction("Show in folder", lambda: self.manager.show_in_folder(item.id))
            menu.addSeparator()
        menu.addAction("Copy download link", lambda: self.manager.copy_link(item.id))
        if state == DownloadState.COMPLETED:
            menu.addAction("Copy file path", lambda: self.manager.copy_path(item.id))
        menu.addSeparator()
        if item.can_retry():
            menu.addAction("Retry", lambda: self.manager.retry(item.id))
        if item.is_active:
            if item.can_resume():
                menu.addAction("Resume", lambda: self.manager.resume(item.id))
            elif item.can_pause():
                menu.addAction("Pause", lambda: self.manager.pause(item.id))
            menu.addAction("Cancel", lambda: self.manager.cancel(item.id))
        menu.addSeparator()
        menu.addAction("Remove from list", lambda: self.manager.remove(item.id))
        if state == DownloadState.COMPLETED:
            menu.addAction("Delete file", lambda: self.manager.remove(item.id, delete_file=True))
        menu.exec(event.globalPos())


class DownloadPanel(QFrame):
    WIDTH = 400

    def __init__(self, manager, anchor, show_all_callback):
        super().__init__(anchor.window(),
                         Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.manager = manager
        self._anchor = anchor
        self._show_all_callback = show_all_callback
        self.setObjectName("DownloadPanel")
        self.setFixedWidth(self.WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(14, 10, 12, 10)
        title = QLabel("Downloads")
        title.setObjectName("PopupHeader")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(DownloadMiniButton(
            "📂", "Open downloads folder", manager.open_download_folder, self))
        layout.addLayout(header)

        line = QFrame()
        line.setObjectName("PanelDivider")
        line.setFixedHeight(1)
        layout.addWidget(line)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("DownloadScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.rows_layout = QVBoxLayout(container)
        self.rows_layout.setContentsMargins(6, 6, 6, 6)
        self.rows_layout.setSpacing(2)
        self.rows_layout.addStretch()
        self.scroll.setWidget(container)
        self.scroll.viewport().setStyleSheet("background: transparent;")
        container.setStyleSheet("background: transparent;")
        layout.addWidget(self.scroll)

        footer = QLabel("Show all downloads")
        footer.setObjectName("PanelFooter")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setCursor(Qt.CursorShape.PointingHandCursor)
        footer.mousePressEvent = lambda e: self._open_all(e)
        layout.addWidget(footer)

        self._rows = {}
        self._populate()

    def _open_all(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()
            if self._show_all_callback:
                self._show_all_callback()

    def _populate(self):
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._rows = {}

        items = sorted(self.manager.downloads.values(),
                       key=lambda i: (not i.is_active, i.created_at), reverse=True)
        items = items[:8]
        if not items:
            empty = QLabel("No downloads yet")
            empty.setObjectName("DownloadEmpty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rows_layout.insertWidget(0, empty)
        for it in items:
            row = DownloadRow(self.manager, it, self)
            self._rows[it.id] = row
            self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)

        rows_height = sum(
            (self.rows_layout.itemAt(i).sizeHint().height() or 0) + 2
            for i in range(self.rows_layout.count() - 1))
        content_height = max(120, min(rows_height + 16, 380))
        self.scroll.setFixedHeight(content_height)
        self.adjustSize()

    def _on_updated(self, item):
        row = self._rows.get(item.id)
        if row is not None:
            row.refresh()
        elif item.is_active:
            self._populate()
        self._maybe_autoclose()

    def _on_removed(self, item):
        row = self._rows.pop(item.id, None)
        if row is not None:
            row.setParent(None)
            row.deleteLater()
        if not self._rows:
            self.close()

    def _maybe_autoclose(self):
        if not self.isVisible():
            return
        if self.manager.active_count():
            return
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self.close)
        self._close_timer.start(4000)

    def showEvent(self, event):
        PopupDismissFilter.register(self)
        self._populate()
        super().showEvent(event)

    def closeEvent(self, event):
        PopupDismissFilter.unregister(self)
        super().closeEvent(event)


class DownloadToolbarButton(QToolButton):
    def __init__(self, manager, show_all_callback=None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self._show_all_callback = show_all_callback
        self.setObjectName("DownloadButton")
        self.setIcon(icon("download.png"))
        self.setIconSize(QSize(17, 17))
        self.setFixedSize(34, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip("Downloads  (Ctrl+J)")

        self._progress = None
        self._suppress_toggle = False
        self._panel = None
        self._anchor = self

        manager.download_added.connect(self._on_download_added)
        manager.download_updated.connect(self._on_download_updated)
        manager.download_removed.connect(self._on_download_removed)
        manager.history_changed.connect(self._on_history_changed)
        self.clicked.connect(self.toggle_panel)

    def _on_download_added(self, item):
        self._refresh_progress()
        self.update()
        self._show_panel()

    def _on_download_updated(self, item):
        self._refresh_progress()
        self.update()
        if self._panel is not None and self._panel.isVisible():
            self._panel._on_updated(item)

    def _on_download_removed(self, item):
        self._refresh_progress()
        self.update()
        if self._panel is not None and self._panel.isVisible():
            self._panel._on_removed(item)

    def _on_history_changed(self):
        self._refresh_progress()
        self.update()

    def _refresh_progress(self):
        if self.manager.active_count() == 0:
            self._progress = None
        else:
            self._progress = self.manager.overall_progress()

    def _show_panel(self):
        if self._panel is not None and self._panel.isVisible():
            self._panel._populate()
            return
        if self._panel is None:
            self._panel = DownloadPanel(self.manager, self, self._show_all_callback)
        self._reposition_panel()
        self._panel.show()

    def toggle_panel(self):
        if self._suppress_toggle:
            self._suppress_toggle = False
            return
        if self._panel is not None and self._panel.isVisible():
            self._panel.close()
            return
        self._show_panel()

    def _reposition_panel(self):
        if self._panel is None:
            return
        top_left = self.mapToGlobal(QPoint(0, self.height() + 6))
        screen = self.screen().availableGeometry() if self.screen() else None
        x = top_left.x() + self.width() - DownloadPanel.WIDTH
        y = top_left.y()
        if screen:
            x = max(screen.left() + 8, min(x, screen.right() - DownloadPanel.WIDTH - 8))
            y = min(y, screen.bottom() - 200)
        self._panel.move(x, y)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._progress is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            margin = 3.0
            rect = QRectF(margin, margin,
                          self.width() - 2 * margin, self.height() - 2 * margin)
            pen = QPen(QColor("#D8DBE4"), 2.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, -360 * 16)
            pen.setColor(QColor("#6D4FD8"))
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, -int(self._progress * 3.6) * 16)
            painter.end()
        elif self.manager.recently_completed_id is not None and not self.manager.active_count():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#2FA66C"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRect(self.width() - 12, 3, 7, 7))
            painter.end()

    def close_popups(self):
        if self._panel is not None and self._panel.isVisible():
            self._panel.close()
