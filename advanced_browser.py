import os
import sys
import json
import urllib.parse
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox,
    QMessageBox, QMenu, QInputDialog, QToolBar, QTabWidget, QStatusBar,
    QDialog, QSpinBox, QFormLayout, QListWidget, QListWidgetItem,
    QTextEdit, QFrame, QSizePolicy, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QFont

# ── Icon helper ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
ICONS_DIR = BASE_DIR / "style" / "icons"

def icon(name: str) -> QIcon:
    return QIcon(str(ICONS_DIR / name))


# ── Settings Dialog ───────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    """Settings dialog for browser configuration"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_browser = parent
        self.setWindowTitle("Browser Settings")
        self.setMinimumWidth(480)
        self.setWindowIcon(icon("settings.png"))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Settings")
        title.setObjectName("SettingsTitle")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.home_page_input = QLineEdit()
        self.home_page_input.setText(self.parent_browser.settings.get("home_page", "about:home"))
        form_layout.addRow("Home Page:", self.home_page_input)

        self.download_dir = QLineEdit()
        self.download_dir.setText(self.parent_browser.settings.get("download_dir", str(Path.home() / "Downloads")))
        form_layout.addRow("Download Directory:", self.download_dir)

        self.javascript_check = QCheckBox("Enable JavaScript")
        self.javascript_check.setChecked(self.parent_browser.settings.get("javascript_enabled", True))
        form_layout.addRow("", self.javascript_check)

        self.local_storage_check = QCheckBox("Enable Local Storage")
        self.local_storage_check.setChecked(self.parent_browser.settings.get("local_storage_enabled", True))
        form_layout.addRow("", self.local_storage_check)

        self.cookies_check = QCheckBox("Accept Cookies")
        self.cookies_check.setChecked(self.parent_browser.settings.get("cookies_enabled", True))
        form_layout.addRow("", self.cookies_check)

        self.cache_check = QCheckBox("Enable Cache")
        self.cache_check.setChecked(self.parent_browser.settings.get("cache_enabled", True))
        form_layout.addRow("", self.cache_check)

        self.zoom_spin = QSpinBox()
        self.zoom_spin.setMinimum(50)
        self.zoom_spin.setMaximum(200)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setValue(self.parent_browser.settings.get("default_zoom", 100))
        form_layout.addRow("Default Zoom:", self.zoom_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.parent_browser.settings.get("theme", "Dark"))
        form_layout.addRow("Theme:", self.theme_combo)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(reset_btn)

        layout.addLayout(btn_layout)

    def save_settings(self):
        settings = {
            "home_page": self.home_page_input.text(),
            "download_dir": self.download_dir.text(),
            "javascript_enabled": self.javascript_check.isChecked(),
            "local_storage_enabled": self.local_storage_check.isChecked(),
            "cookies_enabled": self.cookies_check.isChecked(),
            "cache_enabled": self.cache_check.isChecked(),
            "default_zoom": self.zoom_spin.value(),
            "theme": self.theme_combo.currentText()
        }
        self.parent_browser.settings = settings
        self.parent_browser.save_settings()
        self.parent_browser.apply_global_settings()
        QMessageBox.information(self, "Saved", "Settings saved successfully!")
        self.accept()

    def reset_settings(self):
        self.home_page_input.setText("about:home")
        self.download_dir.setText(str(Path.home() / "Downloads"))
        self.javascript_check.setChecked(True)
        self.local_storage_check.setChecked(True)
        self.cookies_check.setChecked(True)
        self.cache_check.setChecked(True)
        self.zoom_spin.setValue(100)
        self.theme_combo.setCurrentText("Dark")


# ── Inline Find Bar ───────────────────────────────────────────────────────────
class FindBar(QFrame):
    find_next_signal = pyqtSignal(str, bool)
    close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FindBar")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        search_lbl = QLabel()
        search_lbl.setPixmap(icon("search.png").pixmap(16, 16))
        layout.addWidget(search_lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in page…")
        self.search_input.setObjectName("FindInput")
        self.search_input.returnPressed.connect(self.on_find_next)
        layout.addWidget(self.search_input)

        self.btn_prev = QPushButton("↑")
        self.btn_prev.setFixedWidth(30)
        self.btn_prev.setToolTip("Previous match")
        self.btn_prev.clicked.connect(self.on_find_prev)
        layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("↓")
        self.btn_next.setFixedWidth(30)
        self.btn_next.setToolTip("Next match")
        self.btn_next.clicked.connect(self.on_find_next)
        layout.addWidget(self.btn_next)

        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("Case sensitive")
        layout.addWidget(self.case_check)

        self.btn_close = QPushButton()
        self.btn_close.setIcon(icon("find-close.png"))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setFlat(True)
        self.btn_close.setObjectName("FindClose")
        self.btn_close.clicked.connect(self.close_signal.emit)
        layout.addWidget(self.btn_close)

    def on_find_next(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, False)

    def on_find_prev(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, True)


# ── Custom Web Page (intercepts rhodium:// navigation) ─────────────────────────
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


# ── Main Browser Window ───────────────────────────────────────────────────────
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
        self.downloads_file = self.config_dir / "downloads.json"

        self.bookmarks = self.load_bookmarks()
        self.history   = self.load_history()
        self.settings  = self.load_settings()
        self.downloads = self.load_downloads()

        self.setMenuBar(None)          # No old-style menu bar
        self.init_ui()
        self.apply_global_settings()
        self.setStyleSheet(self.get_stylesheet())

    # ── UI Init ───────────────────────────────────────────────────────────────
    def init_ui(self):
        root = QWidget()
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Navigation toolbar (no classic menubar above it)
        self.toolbar = self.create_toolbar()
        vbox.addWidget(self.toolbar)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        new_tab_btn = QPushButton()
        new_tab_btn.setIcon(icon("plus.png"))
        new_tab_btn.setFixedSize(28, 28)
        new_tab_btn.setFlat(True)
        new_tab_btn.setToolTip("New Tab  (Ctrl+T)")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.tab_widget.setCornerWidget(new_tab_btn, Qt.Corner.TopRightCorner)

        vbox.addWidget(self.tab_widget)

        # Find bar (initially hidden)
        self.find_bar = FindBar()
        self.find_bar.hide()
        self.find_bar.find_next_signal.connect(self.perform_find)
        self.find_bar.close_signal.connect(self.find_bar.hide)
        vbox.addWidget(self.find_bar)

        # Status bar
        self.status_bar   = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(root)

        # Keyboard shortcuts (window-level)
        self._add_shortcut("Ctrl+T",         lambda: self.add_new_tab())
        self._add_shortcut("Ctrl+W",         lambda: self.close_tab(self.tab_widget.currentIndex()))
        self._add_shortcut("Ctrl+L",         self.url_bar.setFocus)
        self._add_shortcut("Ctrl+F",         self.open_find_dialog)
        self._add_shortcut("Ctrl+D",         self.add_bookmark)
        self._add_shortcut("Ctrl+J",         self.show_downloads)
        self._add_shortcut("Ctrl+,",         self.open_settings)
        self._add_shortcut("Ctrl+N",         self.open_new_window)
        self._add_shortcut("Ctrl+Q",         self.close)
        self._add_shortcut("F5",             self.reload_page)
        self._add_shortcut("F11",            self.toggle_fullscreen)
        self._add_shortcut("Ctrl++",         self.zoom_in)
        self._add_shortcut("Ctrl+-",         self.zoom_out)
        self._add_shortcut("Ctrl+0",         self.reset_zoom)
        self._add_shortcut("Alt+Left",       self.go_back)
        self._add_shortcut("Alt+Right",      self.go_forward)
        self._add_shortcut("Ctrl+G",         lambda: self.perform_find(self.find_bar.search_input.text(), False))
        self._add_shortcut("Ctrl+Shift+G",   lambda: self.perform_find(self.find_bar.search_input.text(), True))

        # Open first tab
        self.add_new_tab()

    def _add_shortcut(self, key: str, slot):
        act = QAction(self)
        act.setShortcut(QKeySequence(key))
        act.triggered.connect(slot)
        self.addAction(act)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def create_toolbar(self) -> QToolBar:
        bar = QToolBar("Navigation")
        bar.setObjectName("NavBar")
        bar.setIconSize(QSize(18, 18))
        bar.setMovable(False)
        bar.setFloatable(False)

        def nav_btn(icon_name, tip, slot) -> QPushButton:
            b = QPushButton()
            b.setIcon(icon(icon_name))
            b.setToolTip(tip)
            b.setObjectName("NavBtn")
            b.setFixedSize(34, 34)
            b.clicked.connect(slot)
            return b

        self.btn_back    = nav_btn("back.png",    "Back  (Alt+←)",   self.go_back)
        self.btn_forward = nav_btn("forward.png",  "Forward  (Alt+→)", self.go_forward)
        self.btn_reload  = nav_btn("reload.png",   "Reload  (F5)",     self.reload_page)
        self.btn_stop    = nav_btn("stop.png",     "Stop",             self.stop_loading)
        self.btn_home    = nav_btn("home.png",     "Home",             self.go_home)

        for b in (self.btn_back, self.btn_forward, self.btn_reload,
                  self.btn_stop, self.btn_home):
            bar.addWidget(b)

        bar.addSeparator()

        # URL bar (stretches to fill remaining space)
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("UrlBar")
        self.url_bar.setPlaceholderText("Search the web or type a URL…")
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.setFixedHeight(34)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        bar.addWidget(self.url_bar)

        bar.addSeparator()

        # Bookmark star
        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setIcon(icon("bookmark-empty.png"))
        self.btn_bookmark.setToolTip("Add Bookmark  (Ctrl+D)")
        self.btn_bookmark.setObjectName("NavBtn")
        self.btn_bookmark.setFixedSize(34, 34)
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        bar.addWidget(self.btn_bookmark)

        # History dropdown
        self.btn_history = QPushButton()
        self.btn_history.setIcon(icon("history.png"))
        self.btn_history.setToolTip("History")
        self.btn_history.setObjectName("NavBtn")
        self.btn_history.setFixedSize(34, 34)
        self.btn_history.setMenu(self.create_history_menu())
        bar.addWidget(self.btn_history)

        # Downloads
        self.btn_download = QPushButton()
        self.btn_download.setIcon(icon("download.png"))
        self.btn_download.setToolTip("Downloads  (Ctrl+J)")
        self.btn_download.setObjectName("NavBtn")
        self.btn_download.setFixedSize(34, 34)
        self.btn_download.clicked.connect(self.show_downloads)
        bar.addWidget(self.btn_download)

        # Settings
        self.btn_settings = QPushButton()
        self.btn_settings.setIcon(icon("settings.png"))
        self.btn_settings.setToolTip("Settings  (Ctrl+,)")
        self.btn_settings.setObjectName("NavBtn")
        self.btn_settings.setFixedSize(34, 34)
        self.btn_settings.clicked.connect(self.open_settings)
        bar.addWidget(self.btn_settings)

        # Hamburger menu (all remaining items)
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(icon("menu.png"))
        self.btn_menu.setToolTip("Menu")
        self.btn_menu.setObjectName("NavBtn")
        self.btn_menu.setFixedSize(34, 34)
        self.btn_menu.setMenu(self.create_main_menu())
        bar.addWidget(self.btn_menu)

        return bar

    # ── Menus ─────────────────────────────────────────────────────────────────
    def create_main_menu(self) -> QMenu:
        """Single comprehensive hamburger menu replacing the menu bar."""
        m = QMenu(self)
        m.setObjectName("MainMenu")

        # ---- Navigation ----
        m.addSection("Navigation")
        m.addAction(icon("plus.png"),    "New Tab",           self.add_new_tab).setShortcut(QKeySequence("Ctrl+T"))
        m.addAction(icon("home.png"),    "New Window",        self.open_new_window).setShortcut(QKeySequence("Ctrl+N"))
        m.addAction(icon("reload.png"),  "Reload",            self.reload_page).setShortcut(QKeySequence("F5"))
        m.addAction(icon("stop.png"),    "Stop",              self.stop_loading).setShortcut(QKeySequence("Esc"))

        m.addSeparator()

        # ---- Bookmarks sub-menu ----
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

        # ---- History sub-menu ----
        hist_menu = m.addMenu(icon("history.png"), "History")
        hist_menu.aboutToShow.connect(lambda: self._populate_history_submenu(hist_menu))

        m.addSeparator()

        # ---- Page ----
        m.addSection("Page")
        m.addAction(icon("search.png"),     "Find in Page",        self.open_find_dialog).setShortcut(QKeySequence("Ctrl+F"))
        m.addAction(icon("fullscreen.png"), "Toggle Full Screen",  self.toggle_fullscreen).setShortcut(QKeySequence("F11"))

        # Zoom sub-menu
        zoom_menu = m.addMenu("Zoom")
        zoom_menu.addAction("Zoom In",    self.zoom_in).setShortcut(QKeySequence("Ctrl++"))
        zoom_menu.addAction("Zoom Out",   self.zoom_out).setShortcut(QKeySequence("Ctrl+-"))
        zoom_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut(QKeySequence("Ctrl+0"))

        m.addSeparator()

        # ---- Tools ----
        m.addSection("Tools")
        m.addAction(icon("download.png"),  "Downloads",         self.show_downloads).setShortcut(QKeySequence("Ctrl+J"))
        m.addAction(icon("settings.png"),  "Settings",          self.open_settings).setShortcut(QKeySequence("Ctrl+,"))
        m.addAction(icon("delete.png"),    "Clear Browsing Data", self.clear_browsing_data_prompt)
        m.addAction(icon("developer.png"), "Developer Tools",   self.open_dev_tools_info).setShortcut(QKeySequence("F12"))

        m.addSeparator()

        # ---- File ----
        m.addAction("Open File…", self.open_local_file).setShortcut(QKeySequence("Ctrl+O"))

        m.addSeparator()

        # ---- Help ----
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
        """Rebuild hamburger menu (e.g. after bookmarks change)."""
        self.btn_menu.setMenu(self.create_main_menu())

    # ── Tab management ────────────────────────────────────────────────────────
    def add_new_tab(self, url=None):
        if url is None:
            url = self.settings.get("home_page", "about:home")

        view = QWebEngineView()
        page = RhodiumWebEnginePage(self, view)
        view.setPage(page)
        view.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)

        view.loadStarted.connect(lambda: self.on_load_started(view))
        view.loadProgress.connect(lambda p: self.on_load_progress(p, view))
        view.loadFinished.connect(lambda ok: self.on_load_finished(ok, view))
        view.titleChanged.connect(lambda t: self.on_title_changed(t, view))
        view.urlChanged.connect(lambda u: self.on_url_changed(u, view))
        page.profile().downloadRequested.connect(self.on_download_requested)

        idx = self.tab_widget.addTab(view, "New Tab")
        self.tab_widget.setCurrentIndex(idx)

        if url in ("about:home", "rhodium://home"):
            view.setHtml(self.get_home_page_html(), QUrl("about:blank"))
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
        view = self.tab_widget.widget(index)
        if isinstance(view, QWebEngineView):
            url = view.url().toString()
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)

    # ── Navigation ────────────────────────────────────────────────────────────
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
            view.setHtml(self.get_home_page_html(), QUrl("about:blank"))
        else:
            self._load_in_view(url, view)

    def load_url(self, url: str):
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(self.get_home_page_html(), QUrl("about:blank"))
        else:
            self._load_in_view(url, view)

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
        AdvancedBrowser().show()

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

    # ── Bookmark helpers ──────────────────────────────────────────────────────
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

    # ── History ───────────────────────────────────────────────────────────────
    def add_to_history(self, url: str, title: str):
        if not url or url.startswith(("about:", "data:")):
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

    # ── Find in Page ──────────────────────────────────────────────────────────
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

    # ── Zoom ──────────────────────────────────────────────────────────────────
    def zoom_in(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(round(min(v.zoomFactor() + 0.1, 3.0), 1))

    def zoom_out(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(round(max(v.zoomFactor() - 0.1, 0.2), 1))

    def reset_zoom(self):
        v = self.get_current_view()
        if v: v.setZoomFactor(1.0)

    # ── Settings ──────────────────────────────────────────────────────────────
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

    # ── Downloads ─────────────────────────────────────────────────────────────
    def on_download_requested(self, dl):
        dl_dir = self.settings.get("download_dir", str(Path.home() / "Downloads"))
        dl.setDownloadDirectory(dl_dir)
        dl.setDownloadFileName(dl.suggestedFileName())
        dl.accept()
        self.downloads.append({
            "name": dl.suggestedFileName(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "path": os.path.join(dl_dir, dl.suggestedFileName())
        })
        self.save_downloads()
        self.status_label.setText(f"Downloading: {dl.suggestedFileName()}")

    def load_downloads(self):
        try:
            if self.downloads_file.exists():
                return json.loads(self.downloads_file.read_text())
        except Exception:
            pass
        return []

    def save_downloads(self):
        with open(self.downloads_file, "w") as f:
            json.dump(self.downloads, f, indent=2)

    def show_downloads(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Downloads")
        dlg.setMinimumSize(520, 320)
        layout = QVBoxLayout(dlg)
        lst = QListWidget()
        if self.downloads:
            for dl in reversed(self.downloads):
                lst.addItem(f"{dl['name']}   ({dl['date']})")
        else:
            lst.addItem("No downloads yet.")
        layout.addWidget(lst)
        dlg.exec()

    # ── Web Engine Signals ────────────────────────────────────────────────────
    def on_load_started(self, view):
        if self.get_current_view() == view:
            self.status_label.setText("Loading…")
            idx = self.tab_widget.indexOf(view)
            if idx >= 0:
                self.tab_widget.setTabText(idx, "Loading…")

    def on_load_progress(self, progress, view):
        if self.get_current_view() == view:
            self.status_label.setText(f"Loading… {progress}%")

    def on_load_finished(self, ok, view):
        url   = view.url().toString()
        title = view.title() or url

        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            short = title[:26] + "…" if len(title) > 26 else title
            self.tab_widget.setTabText(idx, short)

        if self.get_current_view() == view:
            self.status_label.setText("Done" if ok else "Failed to load page")
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)

        if ok and url not in ("about:blank", ""):
            self.add_to_history(url, title)

    def on_title_changed(self, title, view):
        idx = self.tab_widget.indexOf(view)
        if idx >= 0:
            short = title[:26] + "…" if len(title) > 26 else title
            self.tab_widget.setTabText(idx, short)

    def on_url_changed(self, url, view):
        url_str = url.toString()
        if self.get_current_view() == view:
            self.url_bar.setText("rhodium://home" if url_str in ("about:blank", "") else url_str)
            self._update_bookmark_icon(url_str)

    # ── About / Shortcuts ─────────────────────────────────────────────────────
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

    # ── Stylesheet ────────────────────────────────────────────────────────────
    def get_stylesheet(self) -> str:
        return """
        /* ── Global ── */
        * { font-family: "Segoe UI", "Inter", Arial, sans-serif; }

        QMainWindow { background: #0a0a0d; }

        /* ── Navigation bar ── */
        QToolBar#NavBar {
            background: #111116;
            border-bottom: 1px solid #1e1e2a;
            padding: 4px 8px;
            spacing: 4px;
        }

        /* ── Navigation icon buttons ── */
        QPushButton#NavBtn {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 4px;
        }
        QPushButton#NavBtn:hover {
            background: #1e1e2a;
        }
        QPushButton#NavBtn:pressed {
            background: #2a2a3a;
        }

        /* ── URL bar ── */
        QLineEdit#UrlBar {
            background: #1a1a22;
            color: #e8e8f0;
            border: 1.5px solid #2a2a38;
            border-radius: 18px;
            padding: 6px 18px;
            font-size: 13px;
            selection-background-color: #3060d0;
        }
        QLineEdit#UrlBar:focus {
            border-color: #3060d0;
            background: #1e1e2c;
        }

        /* ── Tabs ── */
        QTabWidget::pane {
            border: none;
            background: #060609;
        }
        QTabBar {
            background: #111116;
        }
        QTabBar::tab {
            background: #111116;
            color: #7a7a9a;
            border: none;
            border-bottom: 2px solid transparent;
            padding: 8px 18px 8px 14px;
            min-width: 130px;
            font-size: 12px;
        }
        QTabBar::tab:selected {
            background: #060609;
            color: #ffffff;
            border-bottom: 2px solid #3060d0;
        }
        QTabBar::tab:hover:!selected {
            color: #c0c0e0;
            background: #161620;
        }
        QTabBar::close-button {
            image: url(style/icons/close (2).png);
            subcontrol-position: right;
        }
        QTabBar::close-button:hover {
            background: #2a2a3a;
            border-radius: 4px;
        }

        /* ── Status bar ── */
        QStatusBar {
            background: #111116;
            border-top: 1px solid #1e1e2a;
        }
        QLabel#StatusLabel {
            color: #606080;
            font-size: 11px;
            padding: 0 8px;
        }

        /* ── Menus ── */
        QMenu {
            background: #16161e;
            color: #e0e0f0;
            border: 1px solid #2a2a38;
            border-radius: 10px;
            padding: 4px 0;
        }
        QMenu::item {
            padding: 7px 22px 7px 14px;
            border-radius: 6px;
            margin: 1px 4px;
        }
        QMenu::item:selected {
            background: #2a3a6a;
            color: #ffffff;
        }
        QMenu::separator {
            height: 1px;
            background: #2a2a38;
            margin: 4px 10px;
        }
        QMenu::section {
            color: #555570;
            font-size: 10px;
            padding: 4px 14px 2px;
            text-transform: uppercase;
        }

        /* ── Dialogs ── */
        QDialog {
            background: #111116;
            color: #e0e0f0;
            border-radius: 12px;
        }
        QLabel {
            color: #c0c0e0;
        }
        QLabel#SettingsTitle {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
        }
        QLineEdit {
            background: #1a1a24;
            color: #e0e0f0;
            border: 1.5px solid #2a2a38;
            border-radius: 8px;
            padding: 6px 10px;
        }
        QLineEdit:focus {
            border-color: #3060d0;
        }
        QPushButton {
            background: #1e1e2c;
            color: #c0c0e0;
            border: 1px solid #2a2a3c;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 12px;
        }
        QPushButton:hover {
            background: #2a2a3c;
            color: #ffffff;
        }
        QPushButton:pressed {
            background: #3060d0;
            color: #ffffff;
            border-color: #3060d0;
        }
        QPushButton#PrimaryBtn {
            background: #2050b0;
            color: #ffffff;
            border: none;
        }
        QPushButton#PrimaryBtn:hover {
            background: #3060d0;
        }
        QCheckBox { color: #c0c0e0; spacing: 6px; }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1.5px solid #3a3a52;
            background: #1a1a24;
        }
        QCheckBox::indicator:checked {
            background: #3060d0;
            border-color: #3060d0;
        }
        QSpinBox, QComboBox {
            background: #1a1a24;
            color: #e0e0f0;
            border: 1.5px solid #2a2a38;
            border-radius: 8px;
            padding: 5px 8px;
        }
        QSpinBox:focus, QComboBox:focus { border-color: #3060d0; }
        QListWidget {
            background: #1a1a24;
            color: #d0d0e8;
            border: 1px solid #2a2a38;
            border-radius: 8px;
            padding: 4px;
        }
        QListWidget::item:selected { background: #2a3a6a; border-radius: 6px; }
        QTextEdit {
            background: #1a1a24;
            color: #d0d0e8;
            border: 1px solid #2a2a38;
            border-radius: 8px;
        }

        /* ── Find bar ── */
        QFrame#FindBar {
            background: #161620;
            border-top: 1px solid #2a2a38;
            max-height: 44px;
        }
        QLineEdit#FindInput {
            border-radius: 14px;
            padding: 5px 12px;
            max-width: 320px;
        }
        QPushButton#FindClose {
            background: transparent;
            border: none;
            border-radius: 6px;
        }
        QPushButton#FindClose:hover { background: #2a2a3a; }
        """

    # ── Home Page HTML ────────────────────────────────────────────────────────
    def get_home_page_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Rhodium Home</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #000;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    overflow: hidden;
    user-select: none;
  }
  /* Globe */
  .globe {
    width: 80px; height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle at 38% 36%, #1a8fe8 0%, #0e5fbc 55%, #082e6e 100%);
    box-shadow: 0 0 40px rgba(30,110,240,.45), 0 0 0 3px rgba(255,255,255,.08);
    display: flex; align-items: center; justify-content: center;
    font-size: 44px;
    margin-bottom: 36px;
    animation: float 5s ease-in-out infinite;
  }
  @keyframes float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
  }
  /* Search */
  .search-wrap {
    position: relative; width: 560px; margin-bottom: 48px;
  }
  .search-icon {
    position: absolute; left: 20px; top: 50%;
    transform: translateY(-50%);
    color: #555; font-size: 18px; pointer-events: none;
  }
  .search-wrap input {
    width: 100%;
    padding: 16px 56px;
    background: #111;
    border: 1.5px solid #2a2a2a;
    border-radius: 30px;
    color: #fff;
    font-size: 15px;
    outline: none;
    transition: border-color .25s, background .25s;
  }
  .search-wrap input::placeholder { color: #666; }
  .search-wrap input:focus {
    border-color: #3060d0;
    background: #141420;
  }
  /* Quick links */
  .links {
    display: flex; gap: 18px;
  }
  .link {
    display: flex; flex-direction: column; align-items: center;
    gap: 10px; cursor: pointer; text-decoration: none;
    color: #888;
    font-size: 12px; font-weight: 500;
    transition: color .2s;
  }
  .link:hover { color: #fff; }
  .link-box {
    width: 58px; height: 58px;
    background: #111;
    border: 1px solid #222;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    transition: background .2s, border-color .2s, transform .15s;
  }
  .link:hover .link-box {
    background: #1a1a26;
    border-color: #3a3a50;
    transform: translateY(-3px);
  }
  .link-box.dashed {
    border-style: dashed;
    color: #444;
  }
  .link:hover .link-box.dashed { color: #888; }
</style>
</head>
<body>
  <div class="globe">🌐</div>

  <div class="search-wrap">
    <span class="search-icon">🔍</span>
    <input id="q" type="text" placeholder="Search the web or type a URL" autofocus>
  </div>

  <div class="links">
    <div class="link" onclick="nav('https://mail.google.com')">
      <div class="link-box">✉️</div><span>Mail</span>
    </div>
    <div class="link" onclick="nav('https://youtube.com')">
      <div class="link-box">▶️</div><span>Video</span>
    </div>
    <div class="link" onclick="nav('https://github.com')">
      <div class="link-box">&lt;/&gt;</div><span>Dev</span>
    </div>
    <div class="link" onclick="nav('https://news.google.com')">
      <div class="link-box">📰</div><span>News</span>
    </div>
    <div class="link" onclick="nav('https://twitter.com')">
      <div class="link-box">💬</div><span>Social</span>
    </div>
    <div class="link" onclick="nav('https://amazon.com')">
      <div class="link-box">🛍️</div><span>Shop</span>
    </div>
    <div class="link" onclick="nav('https://figma.com')">
      <div class="link-box">🎨</div><span>Design</span>
    </div>
    <div class="link" onclick="addLink()">
      <div class="link-box dashed">+</div><span>Add</span>
    </div>
  </div>

<script>
  document.getElementById('q').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const v = e.target.value.trim();
      if (v) nav(v);
    }
  });
  function nav(q) {
    window.location.href = 'rhodium://navigate?q=' + encodeURIComponent(q);
  }
  function addLink() {
    const name = prompt('Link name:');
    const url  = prompt('URL:');
    if (url) nav(url);
  }
</script>
</body>
</html>"""


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RHODIUM Browser")
    app.setOrganizationName("Rhodium")
    window = AdvancedBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
