import os
import sys
import json
import threading
import urllib.parse
from pathlib import Path
from datetime import datetime
import time
import subprocess


from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QMessageBox, QMenu, QInputDialog, QToolBar, QTabBar, QStatusBar,
    QDialog, QListWidget, QTextEdit, QSizePolicy, QFileDialog, QToolButton, QApplication, QProgressBar, QListWidgetItem,
    QFrame, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from rhodium.profile_manager import get_web_profile
from PyQt6.QtCore import Qt, QUrl, QSize, QPoint, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QAction, QDesktopServices, QKeySequence, QPixmap

from rhodium.utils import icon
from rhodium.resources import (
    get_stylesheet as resources_get_stylesheet,
    get_home_page_html, get_offline_page_html, get_downloads_page_html,
    get_history_page_html, get_cookie_debugger_page_html, get_bookmarks_page_html,
)
from rhodium.settings_dialog import SettingsDialog
from rhodium.settings_service import get_settings_service, build_search_url, validate_search_url
from rhodium.settings_page import get_settings_page_html
from rhodium.find_bar import FindBar
from rhodium.web_views import RhodiumWebEnginePage, SmoothWebEngineView
from rhodium.download_manager import DownloadManager
from rhodium.download_ui import DownloadToolbarButton
from rhodium.database import get_database
from rhodium.suggestions import SuggestionController, Suggestion
from rhodium.suggestion_popup import SuggestionLineEdit, SuggestionPopup
from rhodium.cookie_manager import CookieManager
from rhodium.fullscreen_controller import FullscreenController


class RhodiumTabBar(QTabBar):
    tabCloseRequested = pyqtSignal(int)
    doubleClickedEmpty = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pinned_count = 0
        self.setElideMode(Qt.TextElideMode.ElideRight)

    def tabSizeHint(self, index):
        if index < self.pinned_count:
            return QSize(36, 32)
        count = self.count()
        normal_count = count - self.pinned_count
        if normal_count <= 0:
            return super().tabSizeHint(index)
        # Get available width for normal tabs
        available_width = self.width() - (self.pinned_count * 36) - 40
        if available_width <= 0:
            available_width = self.parentWidget().width() - (self.pinned_count * 36) - 40
        if available_width > 0:
            w = available_width // normal_count
            w = max(90, min(220, w))
            return QSize(w, 32)
        return QSize(160, 32)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            idx = self.tabAt(event.pos())
            if idx >= 0:
                self.tabCloseRequested.emit(idx)
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.tabAt(event.pos()) < 0:
                self.doubleClickedEmpty.emit()
                return
        super().mouseDoubleClickEvent(event)


class RhodiumTabWidget(QWidget):
    """Chrome-style tab area: a tab strip with responsive sizing, pinned tabs, close/mute actions, context menus, and overflows."""

    tabCloseRequested = pyqtSignal(int)
    currentChanged = pyqtSignal(int)

    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setObjectName("BrowserTabs")

        self.tab_bar = RhodiumTabBar(self)
        self.tab_bar.setObjectName("RhodiumTabBar")
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setUsesScrollButtons(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setElideMode(Qt.TextElideMode.ElideRight)
        self.tab_bar.setIconSize(QSize(16, 16))
        self.tab_bar.setDrawBase(False)
        self.tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.new_tab_button = QToolButton()
        self.new_tab_button.setObjectName("NewTabButton")
        self.new_tab_button.setAutoRaise(True)
        self.new_tab_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.tab_list_button = QToolButton()
        self.tab_list_button.setObjectName("NewTabButton")
        self.tab_list_button.setAutoRaise(True)
        self.tab_list_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tab_list_button.setToolTip("Show All Tabs")

        strip = QWidget()
        strip.setObjectName("TabStrip")
        self.strip = strip
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(6, 0, 6, 0)
        strip_layout.setSpacing(4)
        strip_layout.addWidget(self.tab_bar)
        strip_layout.addWidget(self.new_tab_button)
        strip_layout.addWidget(self.tab_list_button)
        strip_layout.addStretch()

        self.stack = QStackedWidget()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(strip)
        outer.addWidget(self.stack)

        self.tab_bar.currentChanged.connect(self._on_current_changed)
        self.tab_bar.tabCloseRequested.connect(self.tabCloseRequested)
        self.tab_bar.tabMoved.connect(self._on_tab_moved)
        self.tab_bar.doubleClickedEmpty.connect(lambda: self.browser.add_new_tab())
        self.tab_bar.customContextMenuRequested.connect(self._show_tab_context_menu)
        self.tab_list_button.clicked.connect(self._show_all_tabs_popup)

    def chrome_widget(self):
        return self.strip

    def set_chrome_visible(self, visible):
        self.strip.setVisible(visible)

    def _on_current_changed(self, index):
        self.stack.setCurrentIndex(index)
        self.currentChanged.emit(index)

    def _on_tab_moved(self, from_index, to_index):
        is_from_pinned = from_index < self.tab_bar.pinned_count
        is_to_pinned = to_index < self.tab_bar.pinned_count
        if is_from_pinned != is_to_pinned:
            self.tab_bar.blockSignals(True)
            self.tab_bar.moveTab(to_index, from_index)
            self.tab_bar.blockSignals(False)
            return

        widget = self.stack.widget(from_index)
        self.stack.removeWidget(widget)
        self.stack.insertWidget(to_index, widget)
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())

    def tabBar(self):
        return self.tab_bar

    def addTab(self, widget, label=""):
        index = self.stack.addWidget(widget)
        self.tab_bar.addTab(label)
        self.tab_bar.updateGeometry()
        return index

    def removeTab(self, index):
        widget = self.stack.widget(index)
        if widget is None:
            return
        if index < self.tab_bar.pinned_count:
            self.tab_bar.pinned_count = max(0, self.tab_bar.pinned_count - 1)
        self.stack.removeWidget(widget)
        self.tab_bar.removeTab(index)
        self.tab_bar.updateGeometry()

    def widget(self, index):
        return self.stack.widget(index)

    def count(self):
        return self.stack.count()

    def indexOf(self, widget):
        return self.stack.indexOf(widget)

    def currentWidget(self):
        return self.stack.currentWidget()

    def currentIndex(self):
        return self.tab_bar.currentIndex()

    def setCurrentIndex(self, index):
        self.tab_bar.setCurrentIndex(index)

    def setTabText(self, index, text):
        if index < self.tab_bar.pinned_count:
            self.tab_bar.setTabText(index, "")
        else:
            self.tab_bar.setTabText(index, text)

    def setTabToolTip(self, index, text):
        self.tab_bar.setTabToolTip(index, text)

    def setTabIcon(self, index, tab_icon):
        self.tab_bar.setTabIcon(index, tab_icon)

    def pin_tab(self, index):
        if index < 0 or index >= self.count() or index < self.tab_bar.pinned_count:
            return
        target_index = self.tab_bar.pinned_count
        if index != target_index:
            self.tab_bar.blockSignals(True)
            self.tab_bar.moveTab(index, target_index)
            self.tab_bar.blockSignals(False)
            widget = self.stack.widget(index)
            self.stack.removeWidget(widget)
            self.stack.insertWidget(target_index, widget)
            index = target_index

        widget = self.widget(index)
        widget.setProperty("pinned", True)
        self.tab_bar.pinned_count += 1
        self.tab_bar.setTabText(index, "")
        self.tab_bar.setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
        self.tab_bar.setCurrentIndex(index)
        self.tab_bar.updateGeometry()

    def unpin_tab(self, index):
        if index < 0 or index >= self.count() or index >= self.tab_bar.pinned_count:
            return
        widget = self.widget(index)
        widget.setProperty("pinned", False)
        self.tab_bar.pinned_count = max(0, self.tab_bar.pinned_count - 1)
        target_index = self.tab_bar.pinned_count
        if index != target_index:
            self.tab_bar.blockSignals(True)
            self.tab_bar.moveTab(index, target_index)
            self.tab_bar.blockSignals(False)
            widget = self.stack.widget(index)
            self.stack.removeWidget(widget)
            self.stack.insertWidget(target_index, widget)
            index = target_index

        title = widget.title() or "New Tab"
        short = title[:28] + "…" if len(title) > 28 else title
        self.tab_bar.setTabText(index, short)
        self.tab_bar.setCurrentIndex(index)
        self.tab_bar.updateGeometry()

    def move_tab(self, index, target_index):
        if index < 0 or index >= self.count() or target_index < 0 or target_index >= self.count():
            return
        is_from_pinned = index < self.tab_bar.pinned_count
        is_to_pinned = target_index < self.tab_bar.pinned_count
        if is_from_pinned != is_to_pinned:
            return
        self.tab_bar.moveTab(index, target_index)
        widget = self.stack.widget(index)
        self.stack.removeWidget(widget)
        self.stack.insertWidget(target_index, widget)
        self.setCurrentIndex(target_index)

    def close_other_tabs(self, index):
        for i in range(self.count() - 1, -1, -1):
            if i != index:
                self.browser.close_tab(i)

    def close_tabs_to_right(self, index):
        for i in range(self.count() - 1, index, -1):
            self.browser.close_tab(i)

    def _show_all_tabs_popup(self):
        menu = QMenu(self)
        for i in range(self.count()):
            title = self.widget(i).title() or "New Tab"
            act = menu.addAction(self.tab_bar.tabIcon(i), title)
            act.triggered.connect(lambda checked, idx=i: self.setCurrentIndex(idx))
        menu.exec(self.tab_list_button.mapToGlobal(QPoint(0, self.tab_list_button.height())))

    def _show_tab_context_menu(self, pos):
        index = self.tab_bar.tabAt(pos)
        if index < 0:
            menu = QMenu(self)
            menu.addAction("Open New Tab", lambda: self.browser.add_new_tab())
            if self.browser.closed_tabs_stack:
                menu.addAction("Reopen Closed Tab", lambda: self.browser.reopen_closed_tab())
            menu.exec(self.tab_bar.mapToGlobal(pos))
            return

        menu = QMenu(self)
        menu.addAction("Open New Tab", lambda: self.browser.add_new_tab())
        menu.addSeparator()

        view = self.widget(index)
        menu.addAction("Reload Tab", lambda: view.reload())

        url = view.url().toString()
        menu.addAction("Duplicate Tab", lambda: self.browser.add_new_tab(url))
        menu.addSeparator()

        # Mute / Unmute
        is_muted = view.page().isAudioMuted()
        mute_text = "Unmute Tab" if is_muted else "Mute Tab"
        menu.addAction(mute_text, lambda: view.page().setAudioMuted(not is_muted))

        # Pin / Unpin
        is_pinned = view.property("pinned") or False
        pin_text = "Unpin Tab" if is_pinned else "Pin Tab"
        if is_pinned:
            menu.addAction(pin_text, lambda: self.unpin_tab(index))
        else:
            menu.addAction(pin_text, lambda: self.pin_tab(index))
        menu.addSeparator()

        if index > 0 and (not is_pinned or index < self.tab_bar.pinned_count - 1):
            menu.addAction("Move Tab Left", lambda: self.move_tab(index, index - 1))
        if index < self.count() - 1 and (is_pinned or index >= self.tab_bar.pinned_count):
            menu.addAction("Move Tab Right", lambda: self.move_tab(index, index + 1))
        menu.addSeparator()

        menu.addAction("Close Tab", lambda: self.browser.close_tab(index))
        menu.addAction("Close Other Tabs", lambda: self.close_other_tabs(index))
        menu.addAction("Close Tabs to the Right", lambda: self.close_tabs_to_right(index))

        if self.browser.closed_tabs_stack:
            menu.addSeparator()
            menu.addAction("Reopen Closed Tab", lambda: self.browser.reopen_closed_tab())

        menu.exec(self.tab_bar.mapToGlobal(pos))


class AdvancedBrowser(QMainWindow):
    """RHODIUM – Advanced Browser"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RHODIUM Browser")
        self.setWindowIcon(icon("home.png"))
        self.setGeometry(80, 80, 1280, 820)

        # Data paths
        self.config_dir = Path.home() / ".rhodium"
        self.config_dir.mkdir(exist_ok=True)
        self.bookmarks_file = self.config_dir / "bookmarks.json"
        self.history_file   = self.config_dir / "history.json"

        # Centralized settings service — single source of truth for config.
        self.settings_service = get_settings_service()
        self.settings = self.settings_service.data

        self.bookmarks = self.load_bookmarks()
        self.history   = self.load_history()
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.shortcuts = self.load_shortcuts()

        self.download_manager = DownloadManager(self)
        self.closed_tabs_stack = []

        # Local suggestion data (SQLite history + recent searches + bookmarks)
        self.database = get_database()
        self.suggestion_controller = SuggestionController(
            self.database,
            bookmarks_provider=lambda: self.bookmarks,
        )
        self.suggestion_controller.address_enabled_provider = (
            lambda: self.settings_service.get("search.address_bar_suggestions", True)
        )
        self.suggestion_controller.search_enabled_provider = (
            lambda: self.settings_service.get("search.suggestions_enabled", True)
        )

        # Shared home-page search suggestion popup (reused across home tabs)
        self._home_popup = SuggestionPopup(self)
        self._home_suggestions = []
        self._home_popup_view = None
        self._home_popup.activated.connect(self._on_home_suggestion_activated)

        self._downloads_refresh_timer = QTimer(self)
        self._downloads_refresh_timer.setSingleShot(True)
        self._downloads_refresh_timer.setInterval(500)
        self._downloads_refresh_timer.timeout.connect(self.refresh_downloads_tabs)
        self.download_manager.history_changed.connect(self._downloads_refresh_timer.start)
        self.download_manager.download_updated.connect(self._downloads_refresh_timer.start)

        self._cookie_debugger_refresh_timer = QTimer(self)
        self._cookie_debugger_refresh_timer.setSingleShot(True)
        self._cookie_debugger_refresh_timer.setInterval(600)
        self._cookie_debugger_refresh_timer.timeout.connect(self.refresh_cookie_debugger_tabs)

        self.setMenuBar(None)          # No old-style menu bar
        self.init_ui()
        self.settings_service.setting_changed.connect(self._on_setting_changed)
        self.settings_service.settings_reset.connect(self._on_settings_reset)
        self.apply_global_settings()
        self.cookie_manager = CookieManager()
        try:
            self.cookie_manager.cookies_updated.connect(self._cookie_debugger_refresh_timer.start)
        except Exception:
            pass
        self.apply_theme()
        self.setStyleSheet(self.get_stylesheet())

    def _add_shortcut(self, key: str, slot):
        act = QAction(self)
        act.setShortcut(QKeySequence(key))
        act.triggered.connect(slot)
        self.addAction(act)

    def init_ui(self):
        # Frameless window
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint)

        self._drag_pos = QPoint()

        # Central container
        central = QWidget()
        central.setObjectName("BrowserRoot")

        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        root = QWidget()
        root.setObjectName("BrowserSurface")

        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Navigation toolbar
        self.toolbar = self.create_toolbar()
        vbox.addWidget(self.toolbar)

        # TAB SYSTEM
        self.tab_widget = RhodiumTabWidget(self)

        self.tab_widget.new_tab_button.setIcon(icon("plus.png"))
        self.tab_widget.new_tab_button.setIconSize(QSize(16, 16))
        self.tab_widget.new_tab_button.setFixedSize(28, 28)
        self.tab_widget.new_tab_button.setToolTip("New Tab  (Ctrl+T)")
        self.tab_widget.new_tab_button.clicked.connect(lambda: self.add_new_tab())

        self.tab_widget.tab_list_button.setIcon(icon("menu.png"))
        self.tab_widget.tab_list_button.setIconSize(QSize(14, 14))
        self.tab_widget.tab_list_button.setFixedSize(28, 28)

        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        vbox.addWidget(self.tab_widget)

        # FIND BAR
        self.find_bar = FindBar()
        self.find_bar.hide()

        self.find_bar.find_next_signal.connect(self.perform_find)
        self.find_bar.close_signal.connect(self.find_bar.hide)

        vbox.addWidget(self.find_bar)

        # STATUS BAR
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

        # Root
        layout.addWidget(root)
        self.setCentralWidget(central)

        # Keyboard shortcuts
        self._add_shortcut("Ctrl+T",       self.add_new_tab)
        self._add_shortcut(
            "Ctrl+W",
            lambda: self.close_tab(self.tab_widget.currentIndex())
        )
        self._add_shortcut("Ctrl+L",       self.url_bar.setFocus)
        self._add_shortcut("Ctrl+F",       self.open_find_dialog)
        self._add_shortcut("Ctrl+D",       self.add_bookmark)
        self._add_shortcut("Ctrl+J",       self.open_downloads_page)
        self._add_shortcut("Ctrl+H",       self.open_history_page)
        self._add_shortcut("Ctrl+,",       self.open_settings)
        self._add_shortcut("Ctrl+N",       self.open_new_window)
        self._add_shortcut("Ctrl+Q",       self.close)
        self._add_shortcut("F5",           self.reload_page)
        self._add_shortcut("Ctrl++",       self.zoom_in)
        self._add_shortcut("Ctrl+-",       self.zoom_out)
        self._add_shortcut("Ctrl+0",       self.reset_zoom)
        self._add_shortcut("Alt+Left",     self.go_back)
        self._add_shortcut("Alt+Right",    self.go_forward)

        # Tab navigation & reopen shortcuts
        self._add_shortcut("Ctrl+Shift+T", self.reopen_closed_tab)
        self._add_shortcut("Ctrl+Tab", self.next_tab)
        self._add_shortcut("Ctrl+Shift+Tab", self.prev_tab)
        for i in range(1, 9):
            self._add_shortcut(f"Ctrl+{i}", lambda checked, idx=i-1: self.activate_tab_index(idx))
        self._add_shortcut("Ctrl+9", self.activate_last_tab)

        self._add_shortcut(
            "Ctrl+G",
            lambda: self.perform_find(
                self.find_bar.search_input.text(),
                False
            )
        )

        self._add_shortcut(
            "Ctrl+Shift+G",
            lambda: self.perform_find(
                self.find_bar.search_input.text(),
                True
            )
        )

        # Central fullscreen controller (browser F11 + website fullscreen).
        self.fullscreen_controller = FullscreenController(self)

        # First tab
        self.add_new_tab()

    def create_toolbar(self) -> QToolBar:
        bar = QToolBar("Navigation")
        bar.setObjectName("NavBar")

        bar.setIconSize(QSize(16, 16))
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setContentsMargins(4, 0, 4, 0)

        # Set custom layout spacing
        if bar.layout() is not None:
            bar.layout().setSpacing(3)
            bar.layout().setContentsMargins(6, 0, 6, 0)

        def nav_btn(icon_name, tip, slot):
            b = QPushButton()
            b.setIcon(icon(icon_name))
            b.setIconSize(QSize(16, 16))
            b.setToolTip(tip)
            b.setObjectName("NavBtn")
            b.setFixedSize(32, 32)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            return b

        self.btn_back = nav_btn("back.png", "Back  (Alt+←)", self.go_back)
        self.btn_forward = nav_btn("forward.png", "Forward  (Alt+→)", self.go_forward)
        self.btn_reload = nav_btn("reload.png", "Reload  (F5)", self.reload_page)
        self.btn_stop = nav_btn("stop.png", "Stop", self.stop_loading)
        self.btn_home = nav_btn("home.png", "Home", self.go_home)

        for button in (
            self.btn_back,
            self.btn_forward,
            self.btn_reload,
            self.btn_stop,
            self.btn_home,
        ):
            bar.addWidget(button)

        # URL BAR
        self.url_bar = SuggestionLineEdit()
        self.url_bar.setObjectName("UrlBar")
        self.url_bar.set_controller(self.suggestion_controller)
        self.url_bar.suggestion_activated.connect(self._on_address_suggestion_activated)
        self.url_bar.setPlaceholderText("Search the web or enter an address")
        self.url_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.url_bar.setFixedHeight(36)
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.security_label = QLabel()
        self.security_label.setStyleSheet("padding-left: 8px; background: transparent; margin-right: 4px;")
        self.security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        url_layout = QHBoxLayout(self.url_bar)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.addWidget(self.security_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.url_bar.setTextMargins(32, 0, 8, 0)

        bar.addWidget(self.url_bar)

        # BOOKMARK
        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setObjectName("NavBtn")
        self.btn_bookmark.setIcon(icon("bookmark-empty.png"))
        self.btn_bookmark.setIconSize(QSize(16, 16))
        self.btn_bookmark.setFixedSize(32, 32)
        self.btn_bookmark.setToolTip("Add Bookmark  (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        bar.addWidget(self.btn_bookmark)

        # HISTORY
        self.btn_history = QPushButton()
        self.btn_history.setObjectName("NavBtn")
        self.btn_history.setIcon(icon("history.png"))
        self.btn_history.setIconSize(QSize(16, 16))
        self.btn_history.setFixedSize(32, 32)
        self.btn_history.setToolTip("History")
        self.btn_history.setMenu(self.create_history_menu())
        bar.addWidget(self.btn_history)

        # DOWNLOADS
        self.btn_download = DownloadToolbarButton(
            self.download_manager,
            show_all_callback=lambda: self.load_url("rhodium://downloads")
        )
        # Ensure it matches NavBtn dimensions
        self.btn_download.setFixedSize(32, 32)
        bar.addWidget(self.btn_download)

        # MENU
        self.btn_menu = QPushButton()
        self.btn_menu.setObjectName("NavBtn")
        self.btn_menu.setIcon(icon("menu.png"))
        self.btn_menu.setIconSize(QSize(16, 16))
        self.btn_menu.setFixedSize(32, 32)
        self.btn_menu.setToolTip("Menu")
        self.btn_menu.setMenu(self.create_main_menu())
        bar.addWidget(self.btn_menu)

        # Window controls container/layout for perfect resizing/margins
        self.btn_minimize = QPushButton()
        self.btn_minimize.setObjectName("WinMinBtn")
        self.btn_minimize.setIcon(icon("win-minimize.png"))
        self.btn_minimize.setIconSize(QSize(11, 11))
        self.btn_minimize.setFixedSize(30, 30)
        self.btn_minimize.setFlat(True)
        self.btn_minimize.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_minimize.setToolTip("Minimize")
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.clicked.connect(self.showMinimized)

        self.btn_maximize = QPushButton()
        self.btn_maximize.setObjectName("WinMaxBtn")
        if self.isMaximized():
            self.btn_maximize.setIcon(icon("win-restore.png"))
        else:
            self.btn_maximize.setIcon(icon("win-maximize.png"))
        self.btn_maximize.setIconSize(QSize(11, 11))
        self.btn_maximize.setFixedSize(30, 30)
        self.btn_maximize.setFlat(True)
        self.btn_maximize.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_maximize.setToolTip("Maximize / Restore")
        self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_maximize.clicked.connect(lambda: self.toggle_maximize())

        self.btn_close_win = QPushButton()
        self.btn_close_win.setObjectName("WinCloseBtn")
        self.btn_close_win.setIcon(icon("win-close.png"))
        self.btn_close_win.setIconSize(QSize(11, 11))
        self.btn_close_win.setFixedSize(30, 30)
        self.btn_close_win.setFlat(True)
        self.btn_close_win.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_close_win.setToolTip("Close")
        self.btn_close_win.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close_win.clicked.connect(self.close)

        bar.addWidget(self.btn_minimize)
        bar.addWidget(self.btn_maximize)
        bar.addWidget(self.btn_close_win)

        return bar

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setIcon(icon("win-maximize.png"))
            self.setGeometry(80, 80, 1280, 820)
        else:
            self.showMaximized()
            self.btn_maximize.setIcon(icon("win-restore.png"))

    def create_main_menu(self) -> QMenu:
        """Single comprehensive hamburger menu replacing the menu bar."""
        m = QMenu(self)
        m.setObjectName("MainMenu")

        m.addSection("Navigation")
        m.addAction(icon("plus.png"),    "New Tab",           self.add_new_tab).setShortcut(QKeySequence("Ctrl+T"))
        m.addAction(icon("home.png"),    "New Window",        self.open_new_window).setShortcut(QKeySequence("Ctrl+N"))
        m.addAction(icon("reload.png"),  "Reload",            self.reload_page).setShortcut(QKeySequence("F5"))
        m.addAction(icon("stop.png"),    "Stop",              self.stop_loading).setShortcut(QKeySequence("Esc"))

        m.addSeparator()

        bm_menu = m.addMenu(icon("bookmark-empty.png"), "Bookmarks")
        bm_menu.addAction("Add Bookmark",    self.add_bookmark).setShortcut(QKeySequence("Ctrl+D"))
        bm_menu.addAction("Manage Bookmarks", self.manage_bookmarks)
        bm_menu.addAction(icon("bookmark-filled.png"), "Open Bookmarks Page",
                          self.open_bookmarks_page)
        bm_menu.addSeparator()
        if self.bookmarks:
            for bm in self.bookmarks:
                a = bm_menu.addAction(bm["name"])
                a.triggered.connect(lambda checked, u=bm["url"]: self.load_url(u))
        else:
            bm_menu.addAction("No bookmarks yet").setEnabled(False)

        hist_menu = m.addMenu(icon("history.png"), "History")
        hist_menu.aboutToShow.connect(lambda: self._populate_history_submenu(hist_menu))
        hist_menu.addAction(icon("history.png"), "Open History Page",
                            self.open_history_page).setShortcut(QKeySequence("Ctrl+H"))

        m.addSeparator()

        m.addSection("Page")
        m.addAction(icon("search.png"),     "Find in Page",        self.open_find_dialog).setShortcut(QKeySequence("Ctrl+F"))

        zoom_menu = m.addMenu("Zoom")
        zoom_menu.addAction("Zoom In",    self.zoom_in).setShortcut(QKeySequence("Ctrl++"))
        zoom_menu.addAction("Zoom Out",   self.zoom_out).setShortcut(QKeySequence("Ctrl+-"))
        zoom_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut(QKeySequence("Ctrl+0"))

        m.addSeparator()

        m.addSection("Tools")
        m.addAction(icon("download.png"),  "Downloads",         self.open_downloads_page).setShortcut(QKeySequence("Ctrl+J"))
        m.addAction(icon("settings.png"),  "Settings",          self.open_settings).setShortcut(QKeySequence("Ctrl+,"))
        m.addAction("Clear Browsing Data", self.clear_browsing_data_prompt)
        m.addAction("Cookie Debugger",     self.open_cookie_debugger)
        m.addAction(icon("developer.png"), "Developer Tools",   self.open_dev_tools_info).setShortcut(QKeySequence("F12"))

        m.addSeparator()

        m.addAction("Open File…", self.open_local_file).setShortcut(QKeySequence("Ctrl+O"))

        m.addSeparator()

        m.addSection("Help")
        m.addAction(icon("info (2).png"), "About RHODIUM",     self.show_about)
        m.addAction("Keyboard Shortcuts",                        self.show_shortcuts)

        m.addSeparator()
        m.addAction("Exit", self.close).setShortcut(QKeySequence("Ctrl+Q"))

        return m

    def _populate_history_submenu(self, menu: QMenu):
        menu.clear()
        recent = self.history[-15:]
        if not recent:
            menu.addAction("No history").setEnabled(False)
        else:
            for item in reversed(recent):
                title = (item.get("title") or item.get("url", ""))[:45]
                a = menu.addAction(title)
                a.triggered.connect(lambda checked, u=item["url"]: self.load_url(u))
        menu.addSeparator()
        menu.addAction(icon("history.png"), "Open History Page",
                        self.open_history_page)
        menu.addAction("Clear History", self.clear_history)

    def create_history_menu(self) -> QMenu:
        m = QMenu(self)
        m.aboutToShow.connect(lambda: self._populate_history_submenu(m))
        return m

    def update_main_menu(self):
        self.btn_menu.setMenu(self.create_main_menu())

    def add_new_tab(self, url=None, activate=True):
        if url is None:
            url = self.settings_service.get("general.homepage", "about:home")

        view = SmoothWebEngineView()
        view.rhodium_browser = self
        page = RhodiumWebEnginePage(self, view, view, profile=get_web_profile())
        view.setPage(page)

        view.setZoomFactor(self.settings_service.get("general.zoom", 100) / 100.0)

        view.loadStarted.connect(lambda: self.on_load_started(view))
        view.loadProgress.connect(lambda p: self.on_load_progress(p, view))
        view.loadFinished.connect(lambda ok: self.on_load_finished(ok, view))
        view.titleChanged.connect(lambda t: self.on_title_changed(t, view))
        view.urlChanged.connect(lambda u: self.on_url_changed(u, view))
        view.iconChanged.connect(lambda: self.update_tab_icon(view))

        # Right-click link / page context menu.
        view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        view.customContextMenuRequested.connect(
            lambda pos: self._on_view_context_menu(pos, view)
        )
        # target="_blank" / window.open() / new-window navigation requests.
        page.newWindowRequested.connect(self.handle_new_window_request)

        fs = getattr(self, "fullscreen_controller", None)
        if fs is not None:
            fs.attach_view(view)

        idx = self.tab_widget.addTab(view, "New Tab")
        if activate:
            self.tab_widget.setCurrentIndex(idx)
        self.tab_widget.setTabToolTip(idx, "New Tab")

        if url in ("about:home", "rhodium://home", "about:blank", ""):
            view.setHtml(get_home_page_html(self.shortcuts, self._resolve_theme()), QUrl("about:blank"))
            QTimer.singleShot(50, lambda: self.url_bar.setFocus() or self.url_bar.selectAll())
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        elif url.split("?")[0] == "rhodium://history":
            self.show_history_in_view(view)
        elif url.split("?")[0] == "rhodium://cookie-debugger":
            self.show_cookie_debugger_in_view(view)
        elif url.split("?")[0] == "rhodium://bookmarks":
            self.show_bookmarks_in_view(view)
        elif url.split("?")[0] == "rhodium://settings":
            self.show_settings_in_view(view)
        else:
            self._load_in_view(url, view)

        return view

    def close_tab(self, index):
        if index < 0 or index >= self.tab_widget.count():
            return
        view = self.tab_widget.widget(index)
        if not view:
            return

        # Save to closed tabs stack
        url = view.url().toString()
        title = view.title() or url
        if url not in ("about:blank", "about:home", "rhodium://home", ""):
            self.closed_tabs_stack.append({"url": url, "title": title})

        if self.tab_widget.count() > 1:
            fs = getattr(self, "fullscreen_controller", None)
            if fs is not None:
                fs.on_view_closed(view)

            # If closing the active tab, select adjacent tab explicitly
            if index == self.tab_widget.currentIndex():
                new_index = index - 1 if index > 0 else 1
                self.tab_widget.setCurrentIndex(new_index)

            view.deleteLater()
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def reopen_closed_tab(self):
        if self.closed_tabs_stack:
            item = self.closed_tabs_stack.pop()
            self.add_new_tab(item["url"])

    def next_tab(self):
        count = self.tab_widget.count()
        if count > 1:
            self.tab_widget.setCurrentIndex((self.tab_widget.currentIndex() + 1) % count)

    def prev_tab(self):
        count = self.tab_widget.count()
        if count > 1:
            self.tab_widget.setCurrentIndex((self.tab_widget.currentIndex() - 1) % count)

    def activate_tab_index(self, index):
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    def activate_last_tab(self):
        count = self.tab_widget.count()
        if count > 0:
            self.tab_widget.setCurrentIndex(count - 1)

    def tab_changed(self, index):
        if index < 0:
            return
        view = self.tab_widget.widget(index)
        if isinstance(view, QWebEngineView):
            url = view.url().toString()
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)
            self.update_security_indicator(view.url())

    def _load_in_view(self, url_string: str, view: QWebEngineView):
        if url_string.startswith("rhodium://"):
            # Internal Rhodium URLs are intercepted by RhodiumWebEnginePage's
            # acceptNavigationRequest and handled in-process (never handed to
            # the OS).  Let the page route them.
            view.load(QUrl(url_string))
            return
        if not url_string.startswith(("http://", "https://", "file://", "about:")):
            if "." in url_string and " " not in url_string:
                url_string = "https://" + url_string
            else:
                # Unified search — the configured default engine from the
                # central SettingsService drives every search entry point.
                self.database.record_search(url_string.strip())
                url_string = self.settings_service.build_default_search_url(url_string)
        view.load(QUrl(url_string))

    def open_link_new_tab(self, url: str, activate: bool = True):
        """Open ``url`` in a new tab using the existing tab-creation system.

        The new tab automatically receives favicon/title/loading/history
        handling because it goes through ``add_new_tab``.
        """
        if not url:
            return None
        return self.add_new_tab(url, activate=activate)

    def handle_new_window_request(self, request):
        """Handle target="_blank" / window.open() / new-window requests.

        Always opens the request inside Rhodium (a new tab, or a new window for
        window-type requests) instead of letting the OS take over.
        """
        from PyQt6.QtWebEngineCore import QWebEngineNewWindowRequest
        dt = request.destination
        if dt in (QWebEngineNewWindowRequest.DestinationType.InNewWindow,
                  QWebEngineNewWindowRequest.DestinationType.InNewDialog):
            win = self.open_new_window()
            target = win.get_current_view() if win is not None else None
            if target is not None:
                request.openIn(target.page())
            return
        # InNewTab (foreground) vs InNewBackgroundTab.
        activate = (dt == QWebEngineNewWindowRequest.DestinationType.InNewTab)
        view = self.add_new_tab(activate=activate)
        request.openIn(view.page())

    # ── Link / page context menu ─────────────────────────────────────────────
    def _on_view_context_menu(self, pos: QPoint, view):
        """Build a browser-style context menu at ``pos`` for ``view``.

        Re-uses the page's own hit-test context so the built-in link / image /
        selection actions stay enabled exactly as they would in the native
        menu, while adding the conventional link-opening entries.
        """
        from PyQt6.QtWebEngineCore import QWebEnginePage as WEP
        page = view.page()
        menu = QMenu(self)

        # Link actions (enabled only when the context actually is a link).
        link_items = [
            (WEP.WebAction.OpenLinkInThisWindow, "Open Link"),
            (WEP.WebAction.OpenLinkInNewTab, "Open Link in New Tab"),
            (WEP.WebAction.OpenLinkInNewWindow, "Open Link in New Window"),
            (WEP.WebAction.CopyLinkToClipboard, "Copy Link Address"),
            (WEP.WebAction.DownloadLinkToDisk, "Save Link As…"),
        ]
        added_link = False
        for enum, label in link_items:
            action = page.action(enum)
            if action.isEnabled():
                action.setText(label)
                menu.addAction(action)
                added_link = True

        if added_link:
            menu.addSeparator()

        # Standard page actions (kept from the existing native menu behaviour).
        std_items = [
            WEP.WebAction.Back, WEP.WebAction.Forward, WEP.WebAction.Reload,
            WEP.WebAction.Stop, WEP.WebAction.SavePage, WEP.WebAction.ViewSource,
        ]
        for enum in std_items:
            action = page.action(enum)
            if action.isEnabled():
                menu.addAction(action)

        menu.addSeparator()

        edit_items = [
            WEP.WebAction.Undo, WEP.WebAction.Redo, WEP.WebAction.Cut,
            WEP.WebAction.Copy, WEP.WebAction.Paste, WEP.WebAction.SelectAll,
        ]
        for enum in edit_items:
            action = page.action(enum)
            if action.isEnabled():
                menu.addAction(action)

        # Image actions (enabled only on image context).
        img_items = [
            WEP.WebAction.CopyImageUrlToClipboard,
            WEP.WebAction.CopyImageToClipboard,
            WEP.WebAction.DownloadImageToDisk,
        ]
        img_added = False
        for enum in img_items:
            action = page.action(enum)
            if action.isEnabled():
                if not img_added:
                    menu.addSeparator()
                    img_added = True
                menu.addAction(action)

        if menu.isEmpty():
            menu.addAction("(No actions available)")

        global_pos = view.mapToGlobal(pos)
        self._exec_context_menu(menu, global_pos)

    def _exec_context_menu(self, menu, global_pos: QPoint):
        """Show ``menu`` at ``global_pos``, kept inside the screen bounds."""
        screen = QApplication.screenAt(global_pos)
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            size = menu.sizeHint()
            x = global_pos.x()
            y = global_pos.y()
            if x + size.width() > geo.right():
                x = geo.right() - size.width()
            if y + size.height() > geo.bottom():
                y = geo.bottom() - size.height()
            x = max(geo.left(), x)
            y = max(geo.top(), y)
            global_pos = QPoint(x, y)
        menu.exec(global_pos)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(self.shortcuts, self._resolve_theme()), QUrl("about:blank"))
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        elif url.split("?")[0] == "rhodium://history":
            self.show_history_in_view(view)
        elif url.split("?")[0] == "rhodium://cookie-debugger":
            self.show_cookie_debugger_in_view(view)
        elif url.split("?")[0] == "rhodium://bookmarks":
            self.show_bookmarks_in_view(view)
        elif url.split("?")[0] == "rhodium://settings":
            self.show_settings_in_view(view)
        else:
            self._load_in_view(url, view)

    def load_url(self, url: str):
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(self.shortcuts, self._resolve_theme()), QUrl("about:blank"))
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        elif url.split("?")[0] == "rhodium://history":
            self.show_history_in_view(view)
        elif url.split("?")[0] == "rhodium://cookie-debugger":
            self.show_cookie_debugger_in_view(view)
        elif url.split("?")[0] == "rhodium://bookmarks":
            self.show_bookmarks_in_view(view)
        elif url.split("?")[0] == "rhodium://settings":
            self.show_settings_in_view(view)
        else:
            self._load_in_view(url, view)

    def open_downloads_page(self):
        self.load_url("rhodium://downloads")

    def open_history_page(self):
        self.load_url("rhodium://history")

    def open_cookie_debugger(self):
        """Open the cookie debugger internal page in a new tab."""
        self.load_url("rhodium://cookie-debugger")

    def show_downloads_in_view(self, view):
        """Render the internal rhodium://downloads page in a tab."""
        html = get_downloads_page_html(self.download_manager.get_page_data_json())
        view.setHtml(html, QUrl("rhodium://downloads"))
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            self.tab_widget.setTabText(idx, "Downloads")
            self.tab_widget.setTabToolTip(idx, "Downloads")
            self.tab_widget.setTabIcon(idx, icon("download.png"))

    def handle_download_action(self, download_id, action):
        manager = self.download_manager
        if action == "open":
            manager.open_file(download_id)
        elif action == "folder":
            manager.show_in_folder(download_id)
        elif action == "retry":
            manager.retry(download_id)
        elif action == "pause":
            manager.pause(download_id)
        elif action == "resume":
            manager.resume(download_id)
        elif action == "cancel":
            manager.cancel(download_id)
        elif action == "remove":
            manager.remove(download_id)
        elif action == "delete":
            manager.remove(download_id, delete_file=True)
        self.refresh_downloads_tabs()

    def clear_download_history(self):
        self.download_manager.clear_history()
        self.refresh_downloads_tabs()
        self.status_label.setText("Download history cleared.")

    def refresh_downloads_tabs(self):
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                if view.url().toString().split("?")[0] == "rhodium://downloads":
                    html = get_downloads_page_html(
                        self.download_manager.get_page_data_json())
                    view.setHtml(html, QUrl("rhodium://downloads"))

    # ── History page ──────────────────────────────────────────────────────────
    def show_history_in_view(self, view):
        """Render the internal rhodium://history page in a tab."""
        try:
            history = self.database.get_history()
        except Exception:
            history = []
        html = get_history_page_html(json.dumps(history, ensure_ascii=False))
        view.setHtml(html, QUrl("rhodium://history"))
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            self.tab_widget.setTabText(idx, "History")
            self.tab_widget.setTabToolTip(idx, "History")
            self.tab_widget.setTabIcon(idx, icon("history.png"))

    def refresh_history_tabs(self):
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                if view.url().toString().split("?")[0] == "rhodium://history":
                    try:
                        history = self.database.get_history()
                    except Exception:
                        history = []
                    html = get_history_page_html(
                        json.dumps(history, ensure_ascii=False))
                    view.setHtml(html, QUrl("rhodium://history"))

    def handle_history_action(self, url: str, action: str):
        if action == "delete" and url:
            self.database.delete_history_item(url)
            self.refresh_history_tabs()
            self.status_label.setText("History item removed.")
        elif action == "open" and url:
            self.load_url(url)

    def handle_history_clear(self, range_key: str):
        labels = {
            "hour": "the last hour",
            "today": "today's history",
            "yesterday": "today's and yesterday's history",
            "all": "all history",
        }
        label = labels.get(range_key, "history")
        reply = QMessageBox.question(
            self, "Clear History",
            f"Clear {label}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.database.clear_history_range(range_key)
        if range_key == "all":
            self.history = []
            self.save_history()
        self.refresh_history_tabs()
        self.status_label.setText(f"Cleared {label}.")

    # ── Bookmarks page ──────────────────────────────────────────────────
    def open_bookmarks_page(self):
        self.load_url("rhodium://bookmarks")

    def show_bookmarks_in_view(self, view):
        """Render the internal rhodium://bookmarks page in a tab."""
        try:
            bookmarks_json = json.dumps(self.bookmarks, ensure_ascii=False)
        except Exception:
            bookmarks_json = "[]"
        html = get_bookmarks_page_html(bookmarks_json)
        view.setHtml(html, QUrl("rhodium://bookmarks"))
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            self.tab_widget.setTabText(idx, "Bookmarks")
            self.tab_widget.setTabToolTip(idx, "Bookmarks")
            self.tab_widget.setTabIcon(idx, icon("bookmark-filled.png"))

    def refresh_bookmarks_tabs(self):
        """Re-render every open bookmarks tab."""
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                if view.url().toString().split("?")[0] == "rhodium://bookmarks":
                    try:
                        bookmarks_json = json.dumps(self.bookmarks, ensure_ascii=False)
                    except Exception:
                        bookmarks_json = "[]"
                    html = get_bookmarks_page_html(bookmarks_json)
                    view.setHtml(html, QUrl("rhodium://bookmarks"))

    def handle_bookmark_action(self, url: str, action: str):
        if action == "delete" and url:
            self.delete_bookmark(url)
            self.refresh_bookmarks_tabs()
            self.status_label.setText("Bookmark removed.")
        elif action == "open" and url:
            self.load_url(url)

    def delete_bookmark(self, url: str):
        """Remove a bookmark by URL using the existing bookmark list."""
        url = (url or "").strip()
        if not url:
            return
        self.bookmarks = [b for b in self.bookmarks if b.get("url") != url]
        self.save_bookmarks()
        self.update_main_menu()
        self._update_bookmark_icon(url)

    # ── Cookie Debugger ───────────────────────────────────────────────────────
    def _get_cookie_debugger_diagnostics(self):
        """Return dict with live profile diagnostics for the debugger page."""
        try:
            from rhodium.profile_manager import get_profile_manager
            pm = get_profile_manager()
            profile = pm.profile()
            storage = profile.persistentStoragePath() or "Unknown"
            cache = profile.cachePath() or "Unknown"
            try:
                is_off = bool(profile.isOffTheRecord())
            except Exception:
                is_off = False
            profile_type = "Off-the-record" if is_off else "Persistent"
            is_persistent = bool(storage and storage != "Unknown")
            try:
                pol = str(profile.persistentCookiesPolicy).split(".")[-1]
            except Exception:
                pol = "Not exposed by QtWebEngine"
            try:
                ppol = str(profile.persistentPermissionsPolicy).split(".")[-1]  # type: ignore[attr-defined]
            except Exception:
                ppol = "Not exposed by QtWebEngine"
            try:
                has_store = profile.cookieStore() is not None
            except Exception:
                has_store = False
        except Exception as e:
            storage = "Unknown"
            cache = "Unknown"
            profile_type = "Unknown"
            is_persistent = False
            pol = "Unknown"
            ppol = "Not exposed by QtWebEngine"
            has_store = False
        return {
            "profile_type": profile_type,
            "storage_path": storage,
            "cache_path": cache,
            "is_persistent": is_persistent,
            "cookie_connected": has_store,
            "cookies_policy": pol,
            "permissions_policy": ppol,
        }

    def _cookie_to_dict(self, c):
        """Convert a QNetworkCookie to a JSON-serialisable dict."""
        try:
            name = c.name()
            name = name.data().decode() if hasattr(name, "data") else (name.decode() if isinstance(name, bytes) else str(name))
        except Exception:
            name = "Unknown"
        try:
            value = c.value()
            value = value.data().decode() if hasattr(value, "data") else (value.decode() if isinstance(value, bytes) else str(value))
        except Exception:
            value = ""
        try:
            domain = c.domain() or ""
        except Exception:
            domain = ""
        try:
            path = c.path() or "/"
        except Exception:
            path = "/"
        try:
            is_session = bool(c.isSessionCookie())
        except Exception:
            is_session = True
        try:
            secure = bool(c.isSecure())
        except Exception:
            secure = False
        try:
            httponly = bool(c.isHttpOnly())
        except Exception:
            httponly = False
        # SameSite
        try:
            ss = c.sameSitePolicy()
            # QNetworkCookie.SameSite is an enum
            ss_map = {0: "Default", 1: "None", 2: "Lax", 3: "Strict"}
            samesite = ss_map.get(int(ss), str(ss))
        except Exception:
            samesite = "Unknown"
        # Expiration
        expiration = None
        try:
            dt = c.expirationDate()
            if dt is not None and hasattr(dt, "isNull") and not dt.isNull():
                # QDateTime -> convert to ISO
                try:
                    expiration = dt.toString("yyyy-MM-ddThh:mm:ss")
                    # Try to produce ISO with timezone - fallback
                    if hasattr(dt, "toSecsSinceEpoch"):
                        import datetime as _dt
                        secs = dt.toSecsSinceEpoch()
                        expiration = _dt.datetime.fromtimestamp(secs).isoformat()
                except Exception:
                    expiration = str(dt)
            elif dt is not None and not is_session:
                expiration = str(dt)
        except Exception:
            expiration = None
        return {
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
            "is_session": is_session,
            "secure": secure,
            "httponly": httponly,
            "samesite": samesite,
            "expiration": expiration,
        }

    def show_cookie_debugger_in_view(self, view):
        """Render rhodium://cookie-debugger using the live CookieManager data."""
        diagnostics = self._get_cookie_debugger_diagnostics()

        def on_cookies(cookies):
            try:
                dicts = [self._cookie_to_dict(c) for c in (cookies or [])]
                cookies_json = json.dumps(dicts, ensure_ascii=False)
                diag_json = json.dumps(diagnostics, ensure_ascii=False)
                html = get_cookie_debugger_page_html(cookies_json, diag_json)
                # view may have been closed while cookies were loading
                try:
                    view.setHtml(html, QUrl("rhodium://cookie-debugger"))
                except RuntimeError:
                    return
                idx = self.tab_widget.indexOf(view)
                if idx >= 0:
                    self.tab_widget.setTabText(idx, "Cookie Debugger")
                    self.tab_widget.setTabToolTip(idx, "Cookie Debugger — Rhodium")
                    self.tab_widget.setTabIcon(idx, icon("info (2).png"))
            except Exception as e:
                print(f"show_cookie_debugger_in_view error: {e}")

        # Use existing CookieManager — never create a second profile/database
        try:
            if hasattr(self, "cookie_manager") and self.cookie_manager is not None:
                self.cookie_manager.get_all_cookies_async(on_cookies)
            else:
                on_cookies([])
        except Exception:
            on_cookies([])

    def refresh_cookie_debugger_tabs(self):
        """Re-render every open cookie-debugger tab."""
        for i in range(self.tab_widget.count()):
            v = self.tab_widget.widget(i)
            if isinstance(v, QWebEngineView):
                try:
                    if v.url().toString().split("?")[0] == "rhodium://cookie-debugger":
                        self.show_cookie_debugger_in_view(v)
                except Exception:
                    pass

    def handle_cookie_debugger_delete(self, name: str, domain: str, path: str = ""):
        if not name:
            return
        try:
            # Prefer direct delete via manager (handles domain filtering)
            if hasattr(self, "cookie_manager") and self.cookie_manager is not None:
                self.cookie_manager.delete_cookie(name, domain or None)
            # Refresh after a short delay to allow async delete to propagate
            QTimer.singleShot(400, self.refresh_cookie_debugger_tabs)
            self.status_label.setText(f"Deleted cookie: {name}")
        except Exception as e:
            print(f"handle_cookie_debugger_delete error: {e}")

    def handle_cookie_debugger_delete_domain(self, domain: str):
        if not domain:
            return
        reply = QMessageBox.question(
            self, "Delete Cookies",
            f"Delete all cookies for domain '{domain}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if hasattr(self, "cookie_manager") and self.cookie_manager is not None:
                self.cookie_manager.delete_cookies_for_domain(domain)
            QTimer.singleShot(500, self.refresh_cookie_debugger_tabs)
            self.status_label.setText(f"Cleared cookies for {domain}")
        except Exception as e:
            print(f"handle_cookie_debugger_delete_domain error: {e}")

    def handle_cookie_debugger_delete_all(self):
        reply = QMessageBox.question(
            self, "Delete All Cookies",
            "Delete all cookies from Rhodium?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if hasattr(self, "cookie_manager") and self.cookie_manager is not None:
                self.cookie_manager.delete_all_cookies()
            QTimer.singleShot(500, self.refresh_cookie_debugger_tabs)
            self.status_label.setText("All cookies deleted")
        except Exception as e:
            print(f"handle_cookie_debugger_delete_all error: {e}")

    def handle_cookie_debugger_set_test(self, name: str, value: str, domain: str):
        name = (name or "rhodium_test").strip() or "rhodium_test"
        value = value if value is not None else "hello"
        domain = (domain or "").strip()
        try:
            if hasattr(self, "cookie_manager") and self.cookie_manager is not None:
                ok = self.cookie_manager.set_test_cookie(name, value, domain=domain)
                if ok:
                    self.status_label.setText(f"Test cookie set: {name}")
                else:
                    self.status_label.setText("Failed to set test cookie")
            QTimer.singleShot(600, self.refresh_cookie_debugger_tabs)
        except Exception as e:
            print(f"handle_cookie_debugger_set_test error: {e}")
            QTimer.singleShot(600, self.refresh_cookie_debugger_tabs)

    def get_current_view(self):
        return self.tab_widget.currentWidget()

    # ── Suggestion activation ────────────────────────────────────────────────
    def _on_address_suggestion_activated(self, suggestion):
        """A URL/search suggestion was picked from the address bar popup."""
        self.load_url(suggestion.payload)

    def resolve_home_search(self, query: str) -> str:
        """If the home search popup has a highlighted suggestion, use it."""
        if self._home_popup.isVisible():
            suggestion = self._home_popup.selected_suggestion()
            if suggestion is not None:
                self._home_popup.hide()
                return suggestion.payload
        return query

    def hide_home_popup(self):
        self._home_popup.hide()

    def _fetch_remote_suggestions(self, query: str, callback):
        """Fetch suggestions from the configured engine's endpoint (async)."""
        if not self.settings_service.get("search.suggestions_enabled", True):
            callback([])
            return
        url_str = self.settings_service.suggest_url_for(query)
        if not url_str:
            callback([])
            return
        nam = getattr(self, "_suggest_nam", None)
        if nam is None:
            from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
            nam = QNetworkAccessManager(self)
            self._suggest_nam = nam
        from PyQt6.QtNetwork import QNetworkRequest
        req = QNetworkRequest(QUrl(url_str))
        req.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader,
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Rhodium")
        try:
            reply = nam.get(req)
        except Exception:
            callback([])
            return

        def on_finished():
            items = []
            try:
                data = bytes(reply.readAll())
                text = data.decode("utf-8", errors="ignore").strip()
                if text.startswith("["):
                    arr = json.loads(text)
                    if isinstance(arr, list) and len(arr) >= 2 and isinstance(arr[1], list):
                        raw = arr[1]
                    elif isinstance(arr, list):
                        raw = [x for x in arr if isinstance(x, str)]
                    else:
                        raw = []
                    for x in raw[:10]:
                        if isinstance(x, str) and x.strip():
                            items.append(x.strip())
                else:
                    items = [x.strip('"') for x in text.splitlines() if x.strip()]
            except Exception:
                items = []
            finally:
                try:
                    reply.deleteLater()
                except RuntimeError:
                    pass
            callback(items)

        reply.finished.connect(on_finished)

    def show_home_suggestions(self, query: str, view):
        """Show suggestions under the home page search box.

        Local history/recent-search suggestions are combined with remote
        suggestions from the configured search engine when enabled.
        """
        if self.get_current_view() is not view:
            return
        local = self.suggestion_controller.get_search_suggestions(query, limit=8)

        def finalize(remote):
            if self.get_current_view() is not view:
                return
            combined = list(local)
            seen = {s.primary.lower() for s in combined}
            for item in remote:
                if item.lower() in seen:
                    continue
                seen.add(item.lower())
                combined.append(Suggestion(
                    kind="search", primary=item, secondary="Search suggestion",
                    payload=item, icon="search.png"))
                if len(combined) >= 8:
                    break
            if not combined:
                self._home_popup.hide()
                return
            self._home_suggestions = combined
            self._home_popup_view = view
            view.page().runJavaScript(
                "(function(){var r=document.getElementById('q').getBoundingClientRect();"
                "return [r.left, r.top, r.width, r.height];})()",
                self._position_home_popup,
            )

        self._fetch_remote_suggestions(query, finalize)

    def _position_home_popup(self, rect):
        try:
            view = self._home_popup_view
            if not rect or len(rect) < 4 or view is None or not self._home_suggestions:
                return
            zoom = view.zoomFactor()
            left = int(rect[0] * zoom)
            bottom = int((rect[1] + rect[3]) * zoom)
            width = int(rect[2] * zoom)
            global_pos = view.mapToGlobal(QPoint(left, bottom + 6))
            self._home_popup.set_suggestions(self._home_suggestions)
            self._home_popup.show_at(global_pos, max(320, width))
        except RuntimeError:
            # The view/tab was closed while the JS rect query was in flight.
            self.hide_home_popup()

    def handle_home_suggest_key(self, key: str, view):
        """Keyboard events forwarded from the home page search box."""
        if key == "Escape":
            self._home_popup.hide()
        elif key in ("ArrowDown", "ArrowUp") and self._home_popup.isVisible():
            self._home_popup.move_selection(1 if key == "ArrowDown" else -1)

    def _on_home_suggestion_activated(self, suggestion):
        """A previous-search suggestion was clicked in the home popup."""
        self._home_popup.hide()
        self.load_url(suggestion.payload)

    def go_back(self):
        v = self.get_current_view()
        if v: v.back()

    def go_forward(self):
        v = self.get_current_view()
        if v: v.forward()

    def reload_page(self):
        v = self.get_current_view()
        if v: v.reload()

    def stop_loading(self):
        v = self.get_current_view()
        if v: v.stop()

    def go_home(self):
        self.load_url("about:home")

    def open_new_window(self):
        # Imports here to avoid circular imports during direct instantiation
        from rhodium.browser_window import AdvancedBrowser
        from rhodium.window_filter import ResizeMoveFilter
        from PyQt6.QtWidgets import QApplication

        window = AdvancedBrowser()
        event_filter = ResizeMoveFilter(window)
        QApplication.instance().installEventFilter(event_filter)
        window.show()
        return window

    def open_local_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Web Files (*.html *.htm *.pdf);;All Files (*)"
        )
        if path:
            self.load_url("file:///" + path.replace("\\", "/"))

    def open_dev_tools_info(self):
        QMessageBox.information(self, "Developer Tools",
            "Set the environment variable:\n"
            "  QTWEBENGINE_REMOTE_DEBUGGING=9222\n\n"
            "Then open chromium/chrome and navigate to:\n"
            "  http://localhost:9222")

    def _update_bookmark_icon(self, url: str):
        filled = any(bm["url"] == url for bm in self.bookmarks)
        self.btn_bookmark.setIcon(icon("bookmark-filled.png" if filled else "bookmark-empty.png"))

    def add_bookmark(self):
        view = self.get_current_view()
        if not view:
            return
        url   = view.url().toString()
        title = view.title() or url
        if url in ("about:blank", ""):
            url, title = "about:home", "RHODIUM Home"

        name, ok = QInputDialog.getText(self, "Add Bookmark", "Name:", text=title)
        if ok and name and not any(b["url"] == url for b in self.bookmarks):
            self.bookmarks.append({"name": name, "url": url})
            self.save_bookmarks()
            self._update_bookmark_icon(url)
            self.update_main_menu()
            self.status_label.setText(f"Bookmarked: {name}")

    def manage_bookmarks(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Manage Bookmarks")
        dlg.setMinimumSize(480, 320)
        layout = QVBoxLayout(dlg)

        lst = QListWidget()
        for bm in self.bookmarks:
            lst.addItem(f"{bm['name']}  —  {bm['url']}")
        layout.addWidget(lst)

        btns = QHBoxLayout()
        del_btn  = QPushButton()
        del_btn.setIcon(icon("delete.png"))
        del_btn.setToolTip("Delete selected")

        open_btn = QPushButton("Open")
        open_btn.setObjectName("PrimaryBtn")

        def _delete():
            row = lst.currentRow()
            if row >= 0:
                self.bookmarks.pop(row)
                self.save_bookmarks()
                self.update_main_menu()
                dlg.accept()
                self.manage_bookmarks()

        def _open():
            row = lst.currentRow()
            if row >= 0:
                self.load_url(self.bookmarks[row]["url"])
                dlg.accept()

        del_btn.clicked.connect(_delete)
        open_btn.clicked.connect(_open)
        btns.addWidget(del_btn)
        btns.addStretch()
        btns.addWidget(open_btn)
        layout.addLayout(btns)
        dlg.exec()

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as f:
            json.dump(self.bookmarks, f, indent=2)

    def load_bookmarks(self):
        try:
            if self.bookmarks_file.exists():
                return json.loads(self.bookmarks_file.read_text())
        except Exception:
            pass
        return []

    def add_to_history(self, url: str, title: str):
        if not url or url.startswith(("about:", "data:", "rhodium:")):
            return
        if self.history and self.history[-1]["url"] == url:
            return
        self.history.append({"url": url, "title": title or url,
                              "timestamp": datetime.now().isoformat()})
        self.save_history()

    def clear_history(self):
        if QMessageBox.question(self, "Clear History", "Clear all history?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            self.status_label.setText("History cleared.")

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def load_history(self):
        try:
            if self.history_file.exists():
                return json.loads(self.history_file.read_text())
        except Exception:
            pass
        return []

    def clear_browsing_data_prompt(self):
        if QMessageBox.question(self, "Clear Browsing Data",
                                "Clear history, cache and visited links?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            profile = get_web_profile()
            profile.clearAllVisitedLinks()
            profile.clearHttpCache()
            QMessageBox.information(self, "Done", "Browsing data cleared.")

    def open_find_dialog(self):
        self.find_bar.show()
        self.find_bar.search_input.setFocus()
        self.find_bar.search_input.selectAll()

    def perform_find(self, text: str, reverse: bool = False):
        view = self.get_current_view()
        if not view:
            return
        flags = QWebEnginePage.FindFlag(0)
        if reverse:
            flags |= QWebEnginePage.FindFlag.FindBackward
        if self.find_bar.case_check.isChecked():
            flags |= QWebEnginePage.FindFlag.FindCaseSensitively
        view.findText(text, flags)

    def zoom_in(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(round(min(v.zoomFactor() + 0.1, 3.0), 1))

    def zoom_out(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(round(max(v.zoomFactor() - 0.1, 0.2), 1))

    def reset_zoom(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(1.0)

    def open_settings(self):
        self.load_url("rhodium://settings")

    # ── Centralized settings application ────────────────────────────────────
    @staticmethod
    def _resolve_theme() -> str:
        theme = get_settings_service().get("general.theme", "light")
        if theme == "system":
            return "light"
        return theme

    def get_stylesheet(self) -> str:
        accent = self.settings_service.get("appearance.accent_color", "#6D4FD8")
        return resources_get_stylesheet(self._resolve_theme(), accent)

    def _apply_appearance(self):
        try:
            self.btn_home.setVisible(
                bool(self.settings_service.get("appearance.show_home_button", True)))
        except Exception:
            pass


    def apply_theme(self):
        theme = self._resolve_theme()
        accent = self.settings_service.get("appearance.accent_color", "#6D4FD8")
        self.setStyleSheet(resources_get_stylesheet(theme, accent))
        self._apply_appearance()
        self.refresh_internal_pages()

    def apply_web_settings(self):
        profile = get_web_profile()
        s = self.settings_service
        profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
            if s.get("privacy.cache_enabled", True)
            else QWebEngineProfile.HttpCacheType.NoCache
        )
        qs = profile.settings()
        qs.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled,
                        s.get("privacy.javascript_enabled", True))
        qs.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled,
                        s.get("privacy.local_storage_enabled", True))
        qs.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        try:
            if s.get("privacy.cookies_enabled", True):
                profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
            else:
                profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        except Exception:
            pass

    def _apply_zoom_to_tabs(self, zoom):
        for i in range(self.tab_widget.count()):
            v = self.tab_widget.widget(i)
            if isinstance(v, QWebEngineView):
                v.setZoomFactor(max(0.2, min(3.0, zoom / 100.0)))

    def apply_global_settings(self):
        self.apply_web_settings()
        self._apply_zoom_to_tabs(self.settings_service.get("general.zoom", 100))

    def _on_setting_changed(self, key, value):
        try:
            if key == "general.theme" or key.startswith("appearance."):
                self.apply_theme()
            elif key == "general.zoom":
                self._apply_zoom_to_tabs(value)
            elif key.startswith("privacy."):
                self.apply_web_settings()
            elif key in ("general.homepage", "general.newtab_page"):
                self.refresh_home_pages()
            elif key == "search.default_engine":
                self.status_label.setText("Default search engine updated.")
        except RuntimeError:
            pass

    def _on_settings_reset(self):
        self.apply_global_settings()
        self.apply_theme()
        self.refresh_internal_pages()
        self.status_label.setText("Settings restored to defaults.")

    def refresh_internal_pages(self):
        self.refresh_home_pages()
        self.refresh_settings_tabs()

    # ── Settings page rendering ─────────────────────────────────────────────
    def show_settings_in_view(self, view):
        cat = "general"
        try:
            url_str = view.url().toString()
            if "?" in url_str:
                from urllib.parse import parse_qs
                qs = parse_qs(url_str.split("?", 1)[1])
                if "cat" in qs:
                    cat = qs["cat"][0]
        except Exception:
            cat = "general"
        payload = self._build_settings_payload(cat)
        html = get_settings_page_html(payload)
        target = f"rhodium://settings?cat={cat}"
        view.setHtml(html, QUrl(target))
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            self.tab_widget.setTabText(idx, "Settings")
            self.tab_widget.setTabToolTip(idx, "Settings — Rhodium")
            self.tab_widget.setTabIcon(idx, icon("settings.png"))

    def refresh_settings_tabs(self):
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                try:
                    if view.url().toString().split("?")[0] == "rhodium://settings":
                        self.show_settings_in_view(view)
                except Exception:
                    pass

    def _build_settings_payload(self, cat):
        s = self.settings_service.get_all()
        payload = {
            "settings": s,
            "engines": self.settings_service.engines(),
            "theme": self._resolve_theme(),
            "cat": cat,
            "cookies": [],
            "downloads_count": len(self.download_manager.downloads),
            "bookmarks_count": len(self.bookmarks),
        }
        try:
            payload["history_count"] = self.database.history_row_count()
        except Exception:
            payload["history_count"] = 0
        try:
            raw_cookies = list(self.cookie_manager._cookie_cache.values())
        except Exception:
            raw_cookies = []
        try:
            payload["cookies"] = [self._cookie_to_dict(c) for c in raw_cookies]
        except Exception:
            payload["cookies"] = []
        return payload

    # ── Settings action handlers ────────────────────────────────────────────
    def _coerce_setting(self, key, raw):
        default = self.settings_service.get(key)
        if isinstance(default, bool):
            return str(raw).strip().lower() in ("true", "1", "yes", "on")
        if isinstance(default, int):
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None
        if key == "appearance.accent_color":
            raw = str(raw).strip()
            return raw if raw.startswith("#") else "#" + raw
        return raw

    def handle_settings_set(self, cat, key, raw):
        value = self._coerce_setting(key, raw)
        if value is not None:
            self.settings_service.set(key, value)
        self.refresh_internal_pages()

    def handle_settings_reset(self, cat):
        self.settings_service.reset()

    def handle_settings_search_set_default(self, engine_id, cat):
        if engine_id:
            self.settings_service.set_default_engine(engine_id)
        self.refresh_settings_tabs()

    def handle_settings_search_delete(self, engine_id, cat):
        if engine_id:
            self.settings_service.delete_engine(engine_id)
        self.refresh_settings_tabs()

    def handle_settings_search_restore(self, cat):
        self.settings_service.restore_engines()
        self.refresh_settings_tabs()

    def handle_settings_search_add(self, params, cat):
        name = params.get("name", [""])[0]
        url = params.get("url", [""])[0]
        suggest = params.get("suggest", [""])[0]
        keyword = params.get("keyword", [""])[0]
        if validate_search_url(url):
            self.settings_service.add_engine(name, url, suggest, keyword)
        self.refresh_settings_tabs()

    def handle_settings_search_edit(self, params, cat):
        engine_id = params.get("id", [""])[0]
        name = params.get("name", [None])[0]
        url = params.get("url", [None])[0]
        suggest = params.get("suggest", [None])[0]
        keyword = params.get("keyword", [None])[0]
        self.settings_service.edit_engine(engine_id, name=name, search_url=url,
                                          suggest_url=suggest, keyword=keyword)
        self.refresh_settings_tabs()

    def handle_settings_cookie_delete(self, name, domain, cat):
        if name:
            self.cookie_manager.delete_cookie(name, domain or None)
            QTimer.singleShot(400, self.refresh_settings_tabs)

    def handle_settings_cookie_delete_domain(self, domain, cat):
        if domain:
            self.cookie_manager.delete_cookies_for_domain(domain)
            QTimer.singleShot(450, self.refresh_settings_tabs)

    def handle_settings_cookie_clear(self, cat):
        self.cookie_manager.delete_all_cookies()
        QTimer.singleShot(450, self.refresh_settings_tabs)

    def handle_settings_history_clear(self, range_key, cat):
        self.database.clear_history_range(range_key)
        if range_key == "all":
            self.history = []
            self.save_history()
        self.refresh_history_tabs()
        self.refresh_settings_tabs()
        self.status_label.setText("History cleared.")

    def handle_settings_clear_data(self, what, cat):
        if what in ("history", "all"):
            self.database.clear_history()
            self.history = []
            self.save_history()
            self.refresh_history_tabs()
        if what in ("cache", "all"):
            get_web_profile().clearHttpCache()
        if what in ("cookies", "all"):
            self.cookie_manager.delete_all_cookies()
        if what in ("downloads", "all"):
            self.download_manager.clear_history()
            self.refresh_downloads_tabs()
        self.refresh_settings_tabs()
        self.status_label.setText("Browsing data cleared.")

    def handle_settings_downloads_browse(self, cat):
        current = self.settings_service.get("downloads.directory", str(Path.home() / "Downloads"))
        chosen = QFileDialog.getExistingDirectory(self, "Select Download Directory", current)
        if chosen:
            self.settings_service.set("downloads.directory", chosen)
        self.refresh_settings_tabs()

    def handle_settings_downloads_open_folder(self, cat):
        self.download_manager.open_download_folder()
        self.refresh_settings_tabs()

    def handle_settings_downloads_clear(self, cat):
        self.download_manager.clear_history()
        self.refresh_downloads_tabs()
        self.refresh_settings_tabs()

    def handle_settings_bookmarks_open(self, cat):
        self.manage_bookmarks()
        self.refresh_settings_tabs()

    def handle_settings_bookmarks_import(self, cat):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Bookmarks", "", "JSON Files (*.json);;All Files (*)")
        if path:
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
                if isinstance(data, list):
                    added = 0
                    for item in data:
                        if isinstance(item, dict) and item.get("url"):
                            if not any(b["url"] == item["url"] for b in self.bookmarks):
                                self.bookmarks.append({
                                    "name": item.get("name", item["url"]),
                                    "url": item["url"],
                                })
                                added += 1
                    self.save_bookmarks()
                    self.update_main_menu()
                    self.status_label.setText(f"Imported {added} bookmarks.")
            except Exception as e:
                self.status_label.setText("Failed to import bookmarks.")
        self.refresh_settings_tabs()

    def handle_settings_bookmarks_export(self, cat):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Bookmarks", str(Path.home() / "rhodium-bookmarks.json"),
            "JSON Files (*.json)")
        if path:
            try:
                Path(path).write_text(json.dumps(self.bookmarks, indent=2), encoding="utf-8")
                self.status_label.setText("Bookmarks exported.")
            except Exception:
                self.status_label.setText("Failed to export bookmarks.")
        self.refresh_settings_tabs()

    def clear_all_cookies(self):
        """Clear all cookies."""
        if self.cookie_manager:
            self.cookie_manager.delete_all_cookies()
            print("All cookies cleared")

    def clear_domain_cookies(self, domain: str):
        """Clear cookies for specific domain."""
        if self.cookie_manager:
            count = self.cookie_manager.delete_cookies_for_domain(domain)
            print(f"Cleared {count} cookies for {domain}")

    def delete_cookie(self, name: str, domain: str = None):
        """Delete specific cookie."""
        if self.cookie_manager:
            self.cookie_manager.delete_cookie(name, domain)

    def get_cookie_manager(self):
        """Get the CookieManager instance."""
        return self.cookie_manager

    def on_load_started(self, view):
        self.hide_home_popup()
        if self.get_current_view() != view:
            return
        self.status_label.setText("Loading…")
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            self.tab_widget.setTabText(idx, "Loading…")
            self.tab_widget.setTabToolTip(idx, "Loading…")

    def on_load_progress(self, progress, view):
        if self.get_current_view() == view:
            self.status_label.setText(f"Loading… {progress}%")

    def on_load_finished(self, ok, view):
        url = view.url().toString()
        title = view.title() or url
        idx = self.tab_widget.indexOf(view)

        # Record the visit in the local SQLite suggestion database.
        # Internal/invalid URLs are filtered inside record_visit().
        # Run off the UI thread so page loading is never blocked.
        if ok:
            threading.Thread(
                target=self.database.record_visit,
                args=(url, title), daemon=True
            ).start()

        if idx >= 0:
            short = title[:28] + "…" if len(title) > 28 else title
            if not short:
                short = "New Tab"
            self.tab_widget.setTabText(idx, short)
            self.tab_widget.setTabToolTip(idx, title)

        if not ok:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme in ("http", "https") and "rhodium://retry" not in url:
                view.setHtml(get_offline_page_html(url), QUrl(url))
                return

        if self.get_current_view() == view:
            self.status_label.setText("Done" if ok else "Failed to load page")
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)
            self.update_security_indicator(view.url())

        if ok and url not in ("about:blank", "") and "rhodium://home" not in url:
            self.add_to_history(url, title)
        
        self.update_tab_icon(view)

    def on_title_changed(self, title, view):
        idx = self.tab_widget.indexOf(view)
        if idx < 0:
            return
        title = title.strip()
        if not title:
            title = "New Tab"
        short = title[:28] + "…" if len(title) > 28 else title
        self.tab_widget.setTabText(idx, short)
        self.tab_widget.setTabToolTip(idx, title)

    def on_url_changed(self, url, view):
        url_str = url.toString()
        if self.get_current_view() == view:
            self.url_bar.setText("rhodium://home" if url_str in ("about:blank", "") else url_str)
            self._update_bookmark_icon(url_str)
            self.update_security_indicator(url)
        self.update_tab_icon(view)

    def show_about(self):
        QMessageBox.about(self, "About RHODIUM",
            "RHODIUM Browser\n"
            "Built with PyQt6 & QtWebEngine.\n\n"
            "A fast, minimal, dark-mode browser\n"
            "with bookmarks, history, and more.")

    def show_shortcuts(self):
        lines = [
            "Ctrl+T    New Tab",
            "Ctrl+W    Close Tab",
            "Ctrl+N    New Window",
            "Ctrl+D    Add Bookmark",
            "Ctrl+F    Find in Page",
            "Ctrl+G    Find Next",
            "Ctrl+L    Focus URL Bar",
            "Ctrl+J    Downloads",
            "Ctrl++    Zoom In",
            "Ctrl+-    Zoom Out",
            "Ctrl+0    Reset Zoom",
            "F5        Reload",
            "F12       Developer Tools Info",
            "Ctrl+,    Settings",
            "Ctrl+Q    Exit",
            "Alt+←     Go Back",
            "Alt+→     Go Forward",
        ]
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts")
        dlg.setMinimumSize(360, 440)
        layout = QVBoxLayout(dlg)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText("\n".join(lines))
        layout.addWidget(te)
        dlg.exec()

    # ── Shortcuts & Favicons Caching ───────────────────────────────────────────
    def load_shortcuts(self):
        if self.shortcuts_file.exists():
            try:
                return json.loads(self.shortcuts_file.read_text(encoding="utf-8"))
            except Exception as e:
                print("Error loading shortcuts:", e)
        defaults = [
            {"name": "Google", "url": "https://google.com"},
            {"name": "YouTube", "url": "https://youtube.com"},
            {"name": "GitHub", "url": "https://github.com"},
            {"name": "Gmail", "url": "https://mail.google.com"}
        ]
        for d in defaults:
            self.fetch_favicon_async(d["url"])
        return defaults

    def save_shortcuts(self):
        try:
            self.shortcuts_file.write_text(json.dumps(self.shortcuts, indent=2), encoding="utf-8")
        except Exception as e:
            print("Error saving shortcuts:", e)

    def fetch_favicon_async(self, url):
        import threading
        import urllib.request
        from urllib.parse import urlparse
        
        def run():
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
                if not domain:
                    return
                fav_dir = self.config_dir / "favicons"
                fav_dir.mkdir(exist_ok=True)
                cache_path = fav_dir / f"{domain}.png"
                if cache_path.exists():
                    self.update_shortcut_favicon_path(url, str(cache_path))
                    return
                
                fav_url = f"https://www.google.com/s2/favicons?sz=64&domain={domain}"
                req = urllib.request.Request(fav_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = response.read()
                    if data:
                        cache_path.write_bytes(data)
                        self.update_shortcut_favicon_path(url, str(cache_path))
            except Exception as e:
                print("Failed to fetch favicon for", url, e)
                
        threading.Thread(target=run, daemon=True).start()

    def update_shortcut_favicon_path(self, url, path):
        updated = False
        for s in self.shortcuts:
            if s["url"] == url:
                s["favicon"] = path
                updated = True
        if updated:
            self.save_shortcuts()
            QTimer.singleShot(0, self.refresh_home_pages)

    def refresh_home_pages(self):
        theme = self._resolve_theme()
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                url = view.url().toString()
                if url in ("about:home", "rhodium://home", "about:blank", ""):
                    view.setHtml(get_home_page_html(self.shortcuts, theme), QUrl("about:blank"))

    def add_shortcut_dialog(self):
        dlg = ShortcutDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.name_input.text().strip()
            url_str = dlg.url_input.text().strip()
            if not name or not url_str:
                return
            if not (url_str.startswith("http://") or url_str.startswith("https://")):
                url_str = "https://" + url_str
            if any(s["url"] == url_str for s in self.shortcuts):
                QMessageBox.warning(self, "Duplicate Shortcut", "A shortcut with this URL already exists.")
                return
            self.shortcuts.append({"name": name, "url": url_str})
            self.save_shortcuts()
            self.fetch_favicon_async(url_str)
            self.refresh_home_pages()

    def edit_shortcut_dialog(self, target_url):
        shortcut = None
        for s in self.shortcuts:
            if s["url"] == target_url:
                shortcut = s
                break
        if not shortcut:
            return
        dlg = ShortcutDialog(self, shortcut["name"], shortcut["url"])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name = dlg.name_input.text().strip()
            url_str = dlg.url_input.text().strip()
            if not name or not url_str:
                return
            if not (url_str.startswith("http://") or url_str.startswith("https://")):
                url_str = "https://" + url_str
            if url_str != target_url and any(s["url"] == url_str for s in self.shortcuts):
                QMessageBox.warning(self, "Duplicate Shortcut", "A shortcut with this URL already exists.")
                return
            shortcut["name"] = name
            shortcut["url"] = url_str
            if url_str != target_url:
                shortcut["favicon"] = ""
                self.fetch_favicon_async(url_str)
            self.save_shortcuts()
            self.refresh_home_pages()

    def delete_shortcut(self, target_url):
        self.shortcuts = [s for s in self.shortcuts if s["url"] != target_url]
        self.save_shortcuts()
        self.refresh_home_pages()

    # ── Security Indicator & Tab Favicons ───────────────────────────────────────
    def update_security_indicator(self, url):
        scheme = url.scheme()
        
        if scheme == "https":
            icon_name = "secure.png"
            tooltip = "Secure HTTPS connection"
        elif scheme == "http":
            icon_name = "warning.png"
            tooltip = "Unsecure HTTP connection"
        elif scheme in ("about", "rhodium"):
            icon_name = "info (2).png"
            tooltip = "Internal page"
        else:
            icon_name = "info (2).png"
            tooltip = "Local or extension page"

        # Convert your custom QIcon to a QPixmap and scale it to 16x16 pixels
        pixmap = icon(icon_name).pixmap(16, 16)
        
        self.security_label.setPixmap(pixmap)
        self.security_label.setToolTip(tooltip)

    def update_tab_icon(self, view):
        idx = self.tab_widget.indexOf(view)
        if idx < 0:
            return
        url_str = view.url().toString()
        if url_str in ("about:home", "rhodium://home", "about:blank", ""):
            self.tab_widget.setTabIcon(idx, icon("home.png"))
            return
        if url_str.split("?")[0] == "rhodium://downloads":
            self.tab_widget.setTabIcon(idx, icon("download.png"))
            return
        if url_str.split("?")[0] == "rhodium://history":
            self.tab_widget.setTabIcon(idx, icon("history.png"))
            return
        if url_str.split("?")[0] == "rhodium://cookie-debugger":
            self.tab_widget.setTabIcon(idx, icon("info (2).png"))
            return
        if url_str.split("?")[0] == "rhodium://bookmarks":
            self.tab_widget.setTabIcon(idx, icon("bookmark-filled.png"))
            return
        if "google.com/search" in url_str:
            self.tab_widget.setTabIcon(idx, icon("search.png"))
            return
        page_icon = view.icon()
        if page_icon and not page_icon.isNull():
            self.tab_widget.setTabIcon(idx, page_icon)
        else:
            self.tab_widget.setTabIcon(idx, icon("info (2).png"))

class ShortcutDialog(QDialog):
    def __init__(self, parent=None, name="", url=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Shortcut" if url else "Add Shortcut")
        self.setMinimumWidth(360)
        self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(name)
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setText(url)
        layout.addWidget(self.url_input)
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("PrimaryBtn")
        self.cancel_btn = QPushButton("Cancel")
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
