import os
import sys
import json
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
from PyQt6.QtCore import Qt, QUrl, QSize, QPoint, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QAction, QDesktopServices, QKeySequence, QPixmap

from rhodium.utils import icon
from rhodium.resources import get_stylesheet, get_home_page_html, get_offline_page_html, get_downloads_page_html
from rhodium.settings_dialog import SettingsDialog
from rhodium.find_bar import FindBar
from rhodium.web_views import RhodiumWebEnginePage, SmoothWebEngineView
from rhodium.download_manager import DownloadManager
from rhodium.download_ui import DownloadToolbarButton


class RhodiumTabWidget(QWidget):
    """Chrome-style tab area: a tab strip with an inline '+' button above a page stack."""

    tabCloseRequested = pyqtSignal(int)
    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BrowserTabs")

        self.tab_bar = QTabBar()
        self.tab_bar.setObjectName("RhodiumTabBar")
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setUsesScrollButtons(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setElideMode(Qt.TextElideMode.ElideRight)
        self.tab_bar.setIconSize(QSize(16, 16))
        self.tab_bar.setDrawBase(False)

        self.new_tab_button = QToolButton()
        self.new_tab_button.setObjectName("NewTabButton")
        self.new_tab_button.setAutoRaise(True)
        self.new_tab_button.setCursor(Qt.CursorShape.PointingHandCursor)

        strip = QWidget()
        strip.setObjectName("TabStrip")
        strip_layout = QHBoxLayout(strip)
        strip_layout.setContentsMargins(6, 0, 6, 0)
        strip_layout.setSpacing(4)
        strip_layout.addWidget(self.tab_bar)
        strip_layout.addWidget(self.new_tab_button)
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

    def _on_current_changed(self, index):
        self.stack.setCurrentIndex(index)
        self.currentChanged.emit(index)

    def _on_tab_moved(self, from_index, to_index):
        widget = self.stack.widget(from_index)
        self.stack.removeWidget(widget)
        self.stack.insertWidget(to_index, widget)
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())

    def tabBar(self):
        return self.tab_bar

    def addTab(self, widget, label=""):
        index = self.stack.addWidget(widget)
        self.tab_bar.addTab(label)
        return index

    def removeTab(self, index):
        widget = self.stack.widget(index)
        if widget is None:
            return
        self.stack.removeWidget(widget)
        self.tab_bar.removeTab(index)

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
        self.tab_bar.setTabText(index, text)

    def setTabToolTip(self, index, text):
        self.tab_bar.setTabToolTip(index, text)

    def setTabIcon(self, index, tab_icon):
        self.tab_bar.setTabIcon(index, tab_icon)


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
        self.settings_file  = self.config_dir / "settings.json"

        self.bookmarks = self.load_bookmarks()
        self.history   = self.load_history()
        self.settings  = self.load_settings()
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.shortcuts = self.load_shortcuts()

        self.download_manager = DownloadManager(self)

        self.setMenuBar(None)          # No old-style menu bar
        self.init_ui()
        self.apply_global_settings()
        self.setStyleSheet(self.get_stylesheet())

    def _add_shortcut(self, key: str, slot):
        act = QAction(self)
        act.setShortcut(QKeySequence(key))
        act.triggered.connect(slot)
        self.addAction(act)

    def init_ui(self):
        # Frameless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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
        self.tab_widget = RhodiumTabWidget()

        self.tab_widget.new_tab_button.setIcon(icon("plus.png"))
        self.tab_widget.new_tab_button.setIconSize(QSize(16, 16))
        self.tab_widget.new_tab_button.setFixedSize(28, 28)
        self.tab_widget.new_tab_button.setToolTip("New Tab  (Ctrl+T)")
        self.tab_widget.new_tab_button.clicked.connect(lambda: self.add_new_tab())

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
        self._add_shortcut("Ctrl+,",       self.open_settings)
        self._add_shortcut("Ctrl+N",       self.open_new_window)
        self._add_shortcut("Ctrl+Q",       self.close)
        self._add_shortcut("F5",           self.reload_page)
        self._add_shortcut("F11",          self.toggle_fullscreen)
        self._add_shortcut("Ctrl++",       self.zoom_in)
        self._add_shortcut("Ctrl+-",       self.zoom_out)
        self._add_shortcut("Ctrl+0",       self.reset_zoom)
        self._add_shortcut("Alt+Left",     self.go_back)
        self._add_shortcut("Alt+Right",    self.go_forward)

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

        # First tab
        self.add_new_tab()

    def create_toolbar(self) -> QToolBar:
        bar = QToolBar("Navigation")
        bar.setObjectName("NavBar")

        bar.setIconSize(QSize(17, 17))
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setContentsMargins(4, 0, 4, 0)

        def nav_btn(icon_name, tip, slot):
            b = QPushButton()
            b.setIcon(icon(icon_name))
            b.setIconSize(QSize(17, 17))
            b.setToolTip(tip)
            b.setObjectName("NavBtn")
            b.setFixedSize(34, 34)
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

        bar.addSeparator()

        # URL BAR
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("UrlBar")
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.url_bar.setFixedHeight(36)
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.security_label = QLabel()
        self.security_label.setStyleSheet("padding-left: 8px; font-size: 14px; background: transparent; margin-right: 4px;")
        self.security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        url_layout = QHBoxLayout(self.url_bar)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.addWidget(self.security_label, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.url_bar.setTextMargins(30, 0, 0, 0)

        bar.addWidget(self.url_bar)

        bar.addSeparator()

        # BOOKMARK
        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setObjectName("NavBtn")
        self.btn_bookmark.setIcon(icon("bookmark-empty.png"))
        self.btn_bookmark.setIconSize(QSize(17, 17))
        self.btn_bookmark.setFixedSize(34, 34)
        self.btn_bookmark.setToolTip("Add Bookmark  (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        bar.addWidget(self.btn_bookmark)

        # HISTORY
        self.btn_history = QPushButton()
        self.btn_history.setObjectName("NavBtn")
        self.btn_history.setIcon(icon("history.png"))
        self.btn_history.setIconSize(QSize(17, 17))
        self.btn_history.setFixedSize(34, 34)
        self.btn_history.setToolTip("History")
        self.btn_history.setMenu(self.create_history_menu())
        bar.addWidget(self.btn_history)

        # DOWNLOADS
        self.btn_download = DownloadToolbarButton(
            self.download_manager,
            show_all_callback=lambda: self.load_url("rhodium://downloads")
        )
        bar.addWidget(self.btn_download)

        # MENU
        self.btn_menu = QPushButton()
        self.btn_menu.setObjectName("NavBtn")
        self.btn_menu.setIcon(icon("menu.png"))
        self.btn_menu.setIconSize(QSize(17, 17))
        self.btn_menu.setFixedSize(34, 34)
        self.btn_menu.setToolTip("Menu")
        self.btn_menu.setMenu(self.create_main_menu())
        bar.addWidget(self.btn_menu)

        # APPLICATION BUTTONS
        self.btn_minimize = QPushButton()
        self.btn_minimize.setObjectName("WinMinBtn")
        self.btn_minimize.setIcon(icon("win-minimize.png"))
        self.btn_minimize.setIconSize(QSize(14, 14))
        self.btn_minimize.setFixedSize(34, 34)
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
        self.btn_maximize.setIconSize(QSize(14, 14))
        self.btn_maximize.setFixedSize(34, 34)
        self.btn_maximize.setFlat(True)
        self.btn_maximize.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_maximize.setToolTip("Maximize / Restore")
        self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_maximize.clicked.connect(lambda: self.toggle_maximize())

        self.btn_close_win = QPushButton()
        self.btn_close_win.setObjectName("WinCloseBtn")
        self.btn_close_win.setIcon(icon("win-close.png"))
        self.btn_close_win.setIconSize(QSize(14, 14))
        self.btn_close_win.setFixedSize(34, 34)
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
        bm_menu.addSeparator()
        if self.bookmarks:
            for bm in self.bookmarks:
                a = bm_menu.addAction(bm["name"])
                a.triggered.connect(lambda checked, u=bm["url"]: self.load_url(u))
        else:
            bm_menu.addAction("No bookmarks yet").setEnabled(False)

        hist_menu = m.addMenu(icon("history.png"), "History")
        hist_menu.aboutToShow.connect(lambda: self._populate_history_submenu(hist_menu))

        m.addSeparator()

        m.addSection("Page")
        m.addAction(icon("search.png"),     "Find in Page",        self.open_find_dialog).setShortcut(QKeySequence("Ctrl+F"))
        m.addAction(icon("fullscreen.png"), "Toggle Full Screen",  self.toggle_fullscreen).setShortcut(QKeySequence("F11"))

        zoom_menu = m.addMenu("Zoom")
        zoom_menu.addAction("Zoom In",    self.zoom_in).setShortcut(QKeySequence("Ctrl++"))
        zoom_menu.addAction("Zoom Out",   self.zoom_out).setShortcut(QKeySequence("Ctrl+-"))
        zoom_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut(QKeySequence("Ctrl+0"))

        m.addSeparator()

        m.addSection("Tools")
        m.addAction(icon("download.png"),  "Downloads",         self.open_downloads_page).setShortcut(QKeySequence("Ctrl+J"))
        m.addAction(icon("settings.png"),  "Settings",          self.open_settings).setShortcut(QKeySequence("Ctrl+,"))
        m.addAction(icon("delete.png"),    "Clear Browsing Data", self.clear_browsing_data_prompt)
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
        menu.addAction("Clear History", self.clear_history)

    def create_history_menu(self) -> QMenu:
        m = QMenu(self)
        m.aboutToShow.connect(lambda: self._populate_history_submenu(m))
        return m

    def update_main_menu(self):
        self.btn_menu.setMenu(self.create_main_menu())

    def add_new_tab(self, url=None):
        if url is None:
            url = self.settings.get("home_page", "about:home")

        view = SmoothWebEngineView()
        page = RhodiumWebEnginePage(self, view, view)
        view.setPage(page)

        view.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)

        view.loadStarted.connect(lambda: self.on_load_started(view))
        view.loadProgress.connect(lambda p: self.on_load_progress(p, view))
        view.loadFinished.connect(lambda ok: self.on_load_finished(ok, view))
        view.titleChanged.connect(lambda t: self.on_title_changed(t, view))
        view.urlChanged.connect(lambda u: self.on_url_changed(u, view))
        view.iconChanged.connect(lambda: self.update_tab_icon(view))

        idx = self.tab_widget.addTab(view, "New Tab")
        self.tab_widget.setCurrentIndex(idx)
        self.tab_widget.setTabToolTip(idx, "New Tab")

        if url in ("about:home", "rhodium://home", "about:blank", ""):
            view.setHtml(get_home_page_html(self.shortcuts), QUrl("about:blank"))
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        else:
            self._load_in_view(url, view)

        return view

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            w = self.tab_widget.widget(index)
            w.deleteLater()
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def tab_changed(self, index):
        if index < 0:
            return
        view = self.tab_widget.widget(index)
        if isinstance(view, QWebEngineView):
            url = view.url().toString()
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)

    def _load_in_view(self, url_string: str, view: QWebEngineView):
        if not url_string.startswith(("http://", "https://", "file://", "about:")):
            if "." in url_string and " " not in url_string:
                url_string = "https://" + url_string
            else:
                url_string = "https://www.google.com/search?q=" + urllib.parse.quote_plus(url_string)
        view.load(QUrl(url_string))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(self.shortcuts), QUrl("about:blank"))
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        else:
            self._load_in_view(url, view)

    def load_url(self, url: str):
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(self.shortcuts), QUrl("about:blank"))
        elif url.split("?")[0] == "rhodium://downloads":
            self.show_downloads_in_view(view)
        else:
            self._load_in_view(url, view)

    def open_downloads_page(self):
        self.load_url("rhodium://downloads")

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

    def get_current_view(self):
        return self.tab_widget.currentWidget()

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

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def open_new_window(self):
        # Imports here to avoid circular imports during direct instantiation
        from rhodium.browser_window import AdvancedBrowser
        from rhodium.window_filter import ResizeMoveFilter
        from PyQt6.QtWidgets import QApplication
        
        window = AdvancedBrowser()
        event_filter = ResizeMoveFilter(window)
        QApplication.instance().installEventFilter(event_filter)
        window.show()

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
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()
            QWebEngineProfile.defaultProfile().clearHttpCache()
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
        SettingsDialog(self).exec()

    def load_settings(self):
        try:
            if self.settings_file.exists():
                return json.loads(self.settings_file.read_text())
        except Exception:
            pass
        return {
            "home_page": "about:home",
            "download_dir": str(Path.home() / "Downloads"),
            "ask_where_to_save": False,
            "javascript_enabled": True,
            "local_storage_enabled": True,
            "cookies_enabled": True,
            "cache_enabled": True,
            "default_zoom": 100,
            "theme": "Dark"
        }

    def save_settings(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=2)

    def apply_global_settings(self):
        profile = QWebEngineProfile.defaultProfile()
        try:
            profile.downloadRequested.disconnect()
        except TypeError:
            pass

        profile.downloadRequested.connect(
            self.download_manager.on_download_requested
        )
        profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
            if self.settings.get("cache_enabled", True)
            else QWebEngineProfile.HttpCacheType.NoCache
        )
        s = profile.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled,
                        self.settings.get("javascript_enabled", True))
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled,
                        self.settings.get("local_storage_enabled", True))
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.setStyleSheet(self.get_stylesheet())
        for i in range(self.tab_widget.count()):
            v = self.tab_widget.widget(i)
            if isinstance(v, QWebEngineView):
                v.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)

    def on_load_started(self, view):
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
            "F11       Full Screen",
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

    def get_stylesheet(self) -> str:
        return get_stylesheet()

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
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                url = view.url().toString()
                if url in ("about:home", "rhodium://home", "about:blank", ""):
                    view.setHtml(get_home_page_html(self.shortcuts), QUrl("about:blank"))

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
