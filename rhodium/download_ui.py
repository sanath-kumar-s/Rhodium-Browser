from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, QSize, QObject, QEvent, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import (
    QToolButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGraphicsOpacityEffect, QScrollArea, QApplication, QMenu, QWidget
)

from rhodium.utils import icon
from rhodium.download_manager import (
    DownloadState, format_bytes, format_speed, format_eta
)


def type_badge(filename: str) -> str:
    name = filename.lower()
    if name.endswith((".exe", ".msi", ".msix", ".msp", ".bat", ".cmd", ".ps1", ".scr", ".jar")):
        return "⚙️"
    if name.endswith((".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso")):
        return "📦"
    if name.endswith(".pdf"):
        return "📕"
    if name.endswith((".mp3", ".wav", ".flac", ".ogg", ".m4a")):
        return "🎵"
    if name.endswith((".mp4", ".mkv", ".avi", ".mov", ".webm")):
        return "🎬"
    if name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")):
        return "🖼️"
    if name.endswith((".doc", ".docx", ".txt", ".rtf", ".odt")):
        return "📝"
    if name.endswith((".xls", ".xlsx", ".csv", ".ods")):
        return "📊"
    if name.endswith((".ppt", ".pptx", ".odp")):
        return "📽️"
    if name.endswith((".py", ".js", ".html", ".css", ".json", ".xml", ".ts")):
        return "📜"
    return "📄"


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


class ClickableLabel(QLabel):
    def __init__(self, text, slot, parent=None):
        super().__init__(text, parent)
        self._slot = slot
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._slot()
        super().mouseReleaseEvent(event)


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
                    anchor_rect = QRect(anchor_top_left, anchor.size())
                    if anchor_rect.contains(pos):
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


class DownloadPopupItem(QFrame):
    def __init__(self, manager, item, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.item = item
        self.setObjectName("DownloadPopupItem")

        grid = QVBoxLayout(self)
        grid.setContentsMargins(12, 10, 10, 10)
        grid.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(8)

        self.icon_label = QLabel(type_badge(item.filename))
        self.icon_label.setObjectName("DownloadItemIcon")
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(self.icon_label)

        self.name_label = QLabel(item.filename)
        self.name_label.setObjectName("DownloadItemName")
        top.addWidget(self.name_label, 1)
        grid.addLayout(top)

        self.status_label = QLabel()
        self.status_label.setObjectName("DownloadItemStatus")
        grid.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("DownloadProgressBar")
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        grid.addWidget(self.progress_bar)

        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        self.speed_label = QLabel()
        self.speed_label.setObjectName("DownloadItemSpeed")
        bottom.addWidget(self.speed_label, 1)

        self.btn_pause = DownloadMiniButton("⏸", "Pause", lambda: self.manager.pause(self.item.id), self)
        self.btn_resume = DownloadMiniButton("▶", "Resume", lambda: self.manager.resume(self.item.id), self)
        self.btn_cancel = DownloadMiniButton("✕", "Cancel", lambda: self.manager.cancel(self.item.id), self)
        self.btn_retry = DownloadMiniButton("↻", "Retry", lambda: self.manager.retry(self.item.id), self)
        self.btn_open_file = DownloadMiniButton("↗", "Open", lambda: self.manager.open_file(self.item.id), self)
        self.btn_open = DownloadMiniButton("📂", "Show in folder", lambda: self.manager.show_in_folder(self.item.id), self)
        self.btn_remove = DownloadMiniButton("🗑", "Remove from history", lambda: self.manager.remove(self.item.id), self)

        for b in (self.btn_pause, self.btn_resume, self.btn_cancel,
                  self.btn_retry, self.btn_open_file, self.btn_open, self.btn_remove):
            bottom.addWidget(b)
            b.hide()
        grid.addLayout(bottom)

        if item.executable:
            self.setToolTip("This file is an executable program. "
                            "It will not run automatically.")

    def refresh(self):
        item = self.item
        self.name_label.setText(item.filename)
        if item.state == DownloadState.FAILED and item.error_message:
            self.status_label.setText("Failed — " + item.error_message[:60])
            self.status_label.setToolTip(item.error_message)
        else:
            self.status_label.setText(status_text(item))
            self.status_label.setToolTip("")

        pct = item.percentage
        if item.state in (DownloadState.DOWNLOADING, DownloadState.PAUSED) and pct >= 0:
            self.progress_bar.show()
            self.progress_bar.setValue(pct)
        elif item.state == DownloadState.COMPLETED:
            self.progress_bar.show()
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.hide()

        if item.state == DownloadState.DOWNLOADING:
            speed = format_speed(item.speed)
            eta = format_eta(item.eta)
            self.speed_label.setText(
                f"{speed}   ·   {eta} remaining" if speed else "Starting…")
        elif item.state == DownloadState.PAUSED:
            self.speed_label.setText("Paused")
        else:
            self.speed_label.setText(item.created_at.replace("T", "  "))

        active = item.state in (DownloadState.DOWNLOADING, DownloadState.QUEUED)
        for b, visible in (
            (self.btn_pause, item.state == DownloadState.DOWNLOADING),
            (self.btn_resume, item.state == DownloadState.PAUSED),
            (self.btn_cancel, active),
            (self.btn_retry, item.state in (DownloadState.FAILED,
                                            DownloadState.INTERRUPTED,
                                            DownloadState.CANCELLED)),
            (self.btn_open_file, item.state == DownloadState.COMPLETED),
            (self.btn_open, item.state == DownloadState.COMPLETED),
            (self.btn_remove, not active),
        ):
            b.setVisible(visible)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and \
                self.item.state == DownloadState.COMPLETED:
            self.manager.open_file(self.item.id)
        super().mouseReleaseEvent(event)


class DownloadPopup(QFrame):
    WIDTH = 360
    MAX_HEIGHT = 420

    def __init__(self, manager, anchor):
        super().__init__(anchor.window(),
                         Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.manager = manager
        self._anchor = anchor
        self.setObjectName("DownloadPopup")
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(self.WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QLabel("Downloading")
        self.header.setObjectName("PopupHeader")
        layout.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.items_layout = QVBoxLayout(container)
        self.items_layout.setContentsMargins(6, 6, 6, 6)
        self.items_layout.setSpacing(4)
        self.items_layout.addStretch()
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

        self._items = {}
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self._fade_out)

        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.manager.download_updated.connect(self._on_updated)
        self.manager.download_removed.connect(self._on_removed)

    def add_item(self, item):
        if item.id in self._items:
            return
        widget = DownloadPopupItem(self.manager, item)
        widget.refresh()
        self._items[item.id] = widget
        self.items_layout.insertWidget(self.items_layout.count() - 1, widget)
        self._close_timer.stop()
        self._show_animated()

    def _show_animated(self):
        self._reposition()
        if not self.isVisible():
            self.show()
            self._anim.stop()
            try:
                self._anim.finished.disconnect()
            except TypeError:
                pass
            self._anim.finished.connect(self._noop)
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(1.0)
            self._anim.start()

    def _reposition(self):
        anchor = self._anchor
        content_height = self.sizeHint().height()
        height = max(90, min(content_height, self.MAX_HEIGHT))
        self.setFixedHeight(height)
        top_left = anchor.mapToGlobal(QPoint(0, anchor.height() + 6))
        screen = anchor.screen().availableGeometry() if anchor.screen() else None
        x = top_left.x() + anchor.width() - self.WIDTH
        y = top_left.y()
        if screen:
            x = max(screen.left() + 8, min(x, screen.right() - self.WIDTH - 8))
            y = min(y, screen.bottom() - height - 8)
        self.move(x, y)

    def _on_updated(self, item):
        widget = self._items.get(item.id)
        if widget is None:
            if item.is_active:
                self.add_item(item)
            return
        widget.refresh()
        self.header.setText("Downloading" if self.manager.active_count() else "Downloads")
        if self.manager.active_count():
            self._close_timer.stop()
        elif not self._close_timer.isActive():
            has_failure = any(
                w.item.state in (DownloadState.FAILED, DownloadState.INTERRUPTED)
                for w in self._items.values())
            self._close_timer.start(10000 if has_failure else 4000)
        if self.isVisible():
            self._reposition()

    def _on_removed(self, item):
        widget = self._items.pop(item.id, None)
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        if not self._items:
            self._fade_out()

    def _fade_out(self):
        if not self.isVisible():
            return
        self._anim.stop()
        try:
            self._anim.finished.disconnect()
        except TypeError:
            pass
        self._anim.finished.connect(self.hide)
        self._anim.setStartValue(self._effect.opacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _noop(self):
        pass

    def showEvent(self, event):
        PopupDismissFilter.register(self)
        super().showEvent(event)

    def closeEvent(self, event):
        self._close_timer.stop()
        PopupDismissFilter.unregister(self)
        super().closeEvent(event)


class DownloadMenuRow(QFrame):
    def __init__(self, manager, item, panel, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.item = item
        self.panel = panel
        self.setObjectName("DownloadMenuRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 8, 8)
        row.setSpacing(10)

        icon_label = QLabel(type_badge(item.filename))
        icon_label.setObjectName("DownloadItemIcon")
        icon_label.setFixedSize(26, 26)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(icon_label)

        middle = QVBoxLayout()
        middle.setSpacing(2)
        name = QLabel(item.filename)
        name.setObjectName("DownloadItemName")
        middle.addWidget(name)
        status = QLabel(status_text(item))
        status.setObjectName("DownloadItemStatus")
        middle.addWidget(status)
        if item.state in (DownloadState.DOWNLOADING, DownloadState.PAUSED):
            bar = QProgressBar()
            bar.setObjectName("DownloadProgressBar")
            bar.setFixedHeight(3)
            bar.setTextVisible(False)
            bar.setRange(0, 100)
            bar.setValue(max(0, item.percentage))
            middle.addWidget(bar)
        row.addLayout(middle, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(4)
        if item.state == DownloadState.COMPLETED:
            buttons.addWidget(DownloadMiniButton("↗", "Open", lambda: self._act("open"), self))
            buttons.addWidget(DownloadMiniButton("📂", "Show in folder", lambda: self._act("folder"), self))
        elif item.state in (DownloadState.FAILED, DownloadState.INTERRUPTED, DownloadState.CANCELLED):
            buttons.addWidget(DownloadMiniButton("↻", "Retry", lambda: self._act("retry"), self))
        elif item.is_active:
            buttons.addWidget(DownloadMiniButton("✕", "Cancel", lambda: self._act("cancel"), self))
        row.addLayout(buttons)

    def _act(self, action):
        if action == "open":
            self.manager.open_file(self.item.id)
            self.panel.close()
        elif action == "folder":
            self.manager.show_in_folder(self.item.id)
        elif action == "retry":
            self.manager.retry(self.item.id)
            self.panel.close()
        elif action == "cancel":
            self.manager.cancel(self.item.id)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and \
                self.item.state == DownloadState.COMPLETED:
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
        if state in (DownloadState.FAILED, DownloadState.INTERRUPTED, DownloadState.CANCELLED):
            menu.addAction("Retry", lambda: self.manager.retry(item.id))
        if item.is_active:
            if state == DownloadState.PAUSED:
                menu.addAction("Resume", lambda: self.manager.resume(item.id))
            else:
                menu.addAction("Pause", lambda: self.manager.pause(item.id))
            menu.addAction("Cancel", lambda: self.manager.cancel(item.id))
        menu.addSeparator()
        menu.addAction("Remove from history", lambda: self.manager.remove(item.id))
        if state == DownloadState.COMPLETED:
            menu.addAction("Delete file", lambda: self.manager.remove(item.id, delete_file=True))
        menu.exec(event.globalPos())


class DownloadMenuPanel(QFrame):
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
        header.setContentsMargins(14, 10, 10, 10)
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
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self.rows_layout = QVBoxLayout(container)
        self.rows_layout.setContentsMargins(6, 6, 6, 6)
        self.rows_layout.setSpacing(2)
        self.rows_layout.addStretch()
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

        footer = ClickableLabel("Show all downloads", self._open_all)
        footer.setObjectName("PanelFooter")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        self._populate()

    def _populate(self):
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        recent = sorted(self.manager.downloads.values(),
                        key=lambda i: i.created_at, reverse=True)[:8]
        if not recent:
            empty = QLabel("No downloads yet")
            empty.setObjectName("DownloadEmpty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rows_layout.insertWidget(0, empty)
        for item in recent:
            row = DownloadMenuRow(self.manager, item, self)
            self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)
        rows_height = sum(
            (self.rows_layout.itemAt(i).sizeHint().height() or 0) + 2
            for i in range(self.rows_layout.count() - 1))
        content_height = max(120, min(rows_height + 16, 380))
        self.scroll.setFixedHeight(content_height)
        self.adjustSize()

    def _open_all(self):
        self.close()
        if self._show_all_callback:
            self._show_all_callback()

    def showEvent(self, event):
        self._populate()
        super().showEvent(event)


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
        self._popup = None
        self._panel = None

        manager.download_added.connect(self._on_download_added)
        manager.download_updated.connect(self._on_download_updated)
        manager.download_removed.connect(self._on_download_removed)
        manager.history_changed.connect(self._on_history_changed)
        self.clicked.connect(self.toggle_menu)

    def _on_download_added(self, item):
        self._refresh_progress()
        if self._popup is None:
            self._popup = DownloadPopup(self.manager, self)
        self._popup.add_item(item)
        self.update()

    def _on_download_updated(self, item):
        self._refresh_progress()
        self.update()

    def _on_download_removed(self, item):
        self._refresh_progress()
        self.update()

    def _on_history_changed(self):
        self._refresh_progress()
        self.update()

    def _refresh_progress(self):
        if self.manager.active_count() == 0:
            self._progress = None
        else:
            self._progress = self.manager.overall_progress()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._progress is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            margin = 3.0
            rect = QRectF(margin, margin,
                          self.width() - 2 * margin, self.height() - 2 * margin)
            pen = QPen(QColor("#2b323d"), 2.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, -360 * 16)
            pen.setColor(QColor("#4c8dff"))
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, -int(self._progress * 3.6) * 16)
            painter.end()
        elif self.manager.recently_completed_id is not None and \
                not self.manager.active_count():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor("#3dd68c"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRect(self.width() - 12, 3, 7, 7))
            painter.end()

    def toggle_menu(self):
        if self._suppress_toggle:
            self._suppress_toggle = False
            return
        if self._panel is not None and self._panel.isVisible():
            self._panel.close()
            return
        self.manager.recently_completed_id = None
        self.update()
        self._panel = DownloadMenuPanel(self.manager, self, self._show_all_callback)
        top_left = self.mapToGlobal(QPoint(0, self.height() + 6))
        screen = self.screen().availableGeometry() if self.screen() else None
        x = top_left.x() + self.width() - DownloadMenuPanel.WIDTH
        y = top_left.y()
        if screen:
            x = max(screen.left() + 8, min(x, screen.right() - DownloadMenuPanel.WIDTH - 8))
            y = min(y, screen.bottom() - 200)
        self._panel.move(x, y)
        self._panel.show()

    def close_popups(self):
        if self._popup is not None and self._popup.isVisible():
            self._popup.close()
        if self._panel is not None and self._panel.isVisible():
            self._panel.close()
