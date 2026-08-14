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
    QTextEdit, QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QKeySequence


class SettingsDialog(QDialog):
    """Settings dialog for browser configuration"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_browser = parent
        self.setWindowTitle("Browser Settings")
        self.setMinimumWidth(450)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # General Settings
        self.home_page_input = QLineEdit()
        self.home_page_input.setText(self.parent_browser.settings.get("home_page", "about:home"))
        form_layout.addRow(QLabel("Home Page:"), self.home_page_input)
        
        self.download_dir = QLineEdit()
        self.download_dir.setText(self.parent_browser.settings.get("download_dir", str(Path.home() / "Downloads")))
        form_layout.addRow(QLabel("Download Directory:"), self.download_dir)
        
        # Privacy & Performance Settings
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
        
        # Zoom Level
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setMinimum(50)
        self.zoom_spin.setMaximum(200)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setValue(self.parent_browser.settings.get("default_zoom", 100))
        form_layout.addRow(QLabel("Default Zoom Level:"), self.zoom_spin)
        
        # Theme Setting
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(self.parent_browser.settings.get("theme", "Dark"))
        form_layout.addRow(QLabel("Theme:"), self.theme_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
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
        QMessageBox.information(self, "Settings Saved", "Settings successfully saved!")
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


class FindBar(QFrame):
    """Inline Find-in-page bar that overlay/shows at the bottom"""
    
    find_next_signal = pyqtSignal(str, bool)
    close_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FindBar")
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 4, 10, 4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in page...")
        self.search_input.returnPressed.connect(self.on_find_next)
        layout.addWidget(self.search_input)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self.on_find_next)
        layout.addWidget(self.btn_next)
        
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self.on_find_prev)
        layout.addWidget(self.btn_prev)
        
        self.case_check = QCheckBox("Case Sensitive")
        layout.addWidget(self.case_check)
        
        close_icon_path = os.path.join("style", "icons", "x.png")
        self.btn_close = QPushButton()
        self.btn_close.setIcon(QIcon(close_icon_path))
        self.btn_close.setFlat(True)
        self.btn_close.clicked.connect(self.close_signal.emit)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
        
    def on_find_next(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, False)
            
    def on_find_prev(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, True)


class RhodiumWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage to intercept navigation commands from local html homepage"""
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


class AdvancedBrowser(QMainWindow):
    """Main browser application class"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RHODIUM Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup configs
        self.config_dir = Path.home() / ".rhodium"
        self.config_dir.mkdir(exist_ok=True)
        
        self.bookmarks_file = self.config_dir / "bookmarks.json"
        self.history_file = self.config_dir / "history.json"
        self.settings_file = self.config_dir / "settings.json"
        self.downloads_file = self.config_dir / "downloads.json"
        
        self.bookmarks = self.load_bookmarks()
        self.history = self.load_history()
        self.settings = self.load_settings()
        self.downloads = self.load_downloads()
        
        self.init_ui()
        self.apply_global_settings()
        self.setStyleSheet(self.get_stylesheet())
        
    def init_ui(self):
        # Central widget layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Build URL/Toolbar UI
        self.toolbar = self.create_toolbar()
        self.layout.addWidget(self.toolbar)
        
        # Tabs system
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        # Plus button on tabbar
        self.add_tab_button = QPushButton()
        self.add_tab_button.setIcon(QIcon(os.path.join("style", "icons", "plus.png")))
        self.add_tab_button.setFlat(True)
        self.add_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.tab_widget.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)
        
        self.layout.addWidget(self.tab_widget)
        
        # Find Bar
        self.find_bar = FindBar()
        self.find_bar.hide()
        self.find_bar.find_next_signal.connect(self.perform_find)
        self.find_bar.close_signal.connect(self.find_bar.hide)
        self.layout.addWidget(self.find_bar)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)
        
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        # Initialize Menu Bar
        self.create_menu_bar()
        
        # Add initial tab
        self.add_new_tab()
        
    def create_toolbar(self):
        toolbar = QToolBar("Navigation")
        toolbar.setObjectName("NavBar")
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        
        # Navigation buttons
        self.btn_back = QPushButton()
        self.btn_back.setIcon(QIcon(os.path.join("style", "icons", "arrow-left.png")))
        self.btn_back.setToolTip("Back (Alt+Left)")
        self.btn_back.clicked.connect(self.go_back)
        toolbar.addWidget(self.btn_back)
        
        self.btn_forward = QPushButton()
        self.btn_forward.setIcon(QIcon(os.path.join("style", "icons", "arrow-right.png")))
        self.btn_forward.setToolTip("Forward (Alt+Right)")
        self.btn_forward.clicked.connect(self.go_forward)
        toolbar.addWidget(self.btn_forward)
        
        self.btn_reload = QPushButton()
        self.btn_reload.setIcon(QIcon(os.path.join("style", "icons", "rotate-cw.png")))
        self.btn_reload.setToolTip("Reload (F5)")
        self.btn_reload.clicked.connect(self.reload_page)
        toolbar.addWidget(self.btn_reload)
        
        self.btn_stop = QPushButton()
        self.btn_stop.setIcon(QIcon(os.path.join("style", "icons", "circle-x.png")))
        self.btn_stop.setToolTip("Stop Loading (Esc)")
        self.btn_stop.clicked.connect(self.stop_loading)
        toolbar.addWidget(self.btn_stop)
        
        self.btn_home = QPushButton()
        self.btn_home.setIcon(QIcon(os.path.join("style", "icons", "house.png")))
        self.btn_home.setToolTip("Home")
        self.btn_home.clicked.connect(self.go_home)
        toolbar.addWidget(self.btn_home)
        
        toolbar.addSeparator()
        
        # URL line edit
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search the web or type a URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Bookmark toggle inside or near URL bar
        self.btn_bookmark = QPushButton()
        self.btn_bookmark.setIcon(QIcon(os.path.join("style", "icons", "bookmark.png")))
        self.btn_bookmark.setToolTip("Add Bookmark (Ctrl+D)")
        self.btn_bookmark.clicked.connect(self.add_bookmark)
        toolbar.addWidget(self.btn_bookmark)
        
        # History menu
        self.btn_history = QPushButton()
        self.btn_history.setIcon(QIcon(os.path.join("style", "icons", "rotate-ccw-clock.png")))
        self.btn_history.setToolTip("History")
        self.btn_history.setMenu(self.create_history_menu())
        toolbar.addWidget(self.btn_history)
        
        # Downloads list dialog shortcut
        self.btn_download = QPushButton()
        self.btn_download.setIcon(QIcon(os.path.join("style", "icons", "download.png")))
        self.btn_download.setToolTip("Downloads (Ctrl+J)")
        self.btn_download.clicked.connect(self.show_downloads)
        toolbar.addWidget(self.btn_download)
        
        # Quick menu (hamburger)
        self.btn_menu = QPushButton()
        self.btn_menu.setIcon(QIcon(os.path.join("style", "icons", "menu.png")))
        self.btn_menu.setToolTip("Quick Menu")
        self.btn_menu.setMenu(self.create_quick_menu())
        toolbar.addWidget(self.btn_menu)
        
        return toolbar

    def create_quick_menu(self):
        menu = QMenu(self)
        
        menu.addAction("New Tab", self.add_new_tab).setShortcut("Ctrl+T")
        menu.addAction("New Window", self.open_new_window).setShortcut("Ctrl+N")
        menu.addSeparator()
        menu.addAction("Find in Page", self.open_find_dialog).setShortcut("Ctrl+F")
        menu.addAction("Downloads", self.show_downloads).setShortcut("Ctrl+J")
        menu.addSeparator()
        menu.addAction("Settings", self.open_settings).setShortcut("Ctrl+,")
        menu.addAction("Clear Browsing Data", self.clear_browsing_data_prompt).setShortcut("Ctrl+Shift+Del")
        menu.addSeparator()
        menu.addAction("Exit", self.close).setShortcut("Ctrl+Q")
        
        return menu
        
    def create_history_menu(self):
        menu = QMenu(self)
        menu.aboutToShow.connect(lambda: self.populate_history_menu(menu))
        return menu

    def populate_history_menu(self, menu):
        menu.clear()
        recent = self.history[-10:]
        if not recent:
            menu.addAction("No history recorded").setEnabled(False)
        else:
            for item in reversed(recent):
                title = item.get("title", "") or item.get("url", "")
                action = menu.addAction(title[:40])
                action.triggered.connect(lambda checked, url=item["url"]: self.load_url(url))
        menu.addSeparator()
        menu.addAction("Clear History", self.clear_history)

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Tab", lambda: self.add_new_tab()).setShortcut("Ctrl+T")
        file_menu.addAction("New Window", self.open_new_window).setShortcut("Ctrl+N")
        file_menu.addAction("Open File", self.open_local_file).setShortcut("Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("Downloads", self.show_downloads).setShortcut("Ctrl+J")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close).setShortcut("Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Find in Page", self.open_find_dialog).setShortcut("Ctrl+F")
        edit_menu.addAction("Find Next", lambda: self.perform_find(self.find_bar.search_input.text(), False)).setShortcut("Ctrl+G")
        edit_menu.addAction("Find Previous", lambda: self.perform_find(self.find_bar.search_input.text(), True)).setShortcut("Ctrl+Shift+G")
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Zoom In", self.zoom_in).setShortcut("Ctrl++")
        view_menu.addAction("Zoom Out", self.zoom_out).setShortcut("Ctrl+-")
        view_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut("Ctrl+0")
        view_menu.addSeparator()
        view_menu.addAction("Full Screen", self.toggle_fullscreen).setShortcut("F11")
        view_menu.addAction("Reload", self.reload_page).setShortcut("F5")
        view_menu.addAction("Stop", self.stop_loading).setShortcut("Esc")
        
        # Bookmarks menu
        self.bookmarks_menu = menubar.addMenu("Bookmarks")
        self.update_bookmarks_menu()
        
        # History menu
        self.history_menu = menubar.addMenu("History")
        self.history_menu.aboutToShow.connect(self.update_history_menu)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Settings", self.open_settings).setShortcut("Ctrl+,")
        tools_menu.addAction("Clear Browsing Data", self.clear_browsing_data_prompt).setShortcut("Ctrl+Shift+Del")
        tools_menu.addAction("Developer Tools Info", self.open_dev_tools_info).setShortcut("F12")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About RHODIUM", self.show_about)
        help_menu.addAction("Keyboard Shortcuts", self.show_shortcuts)

    def update_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        self.bookmarks_menu.addAction("Add Bookmark", self.add_bookmark).setShortcut("Ctrl+D")
        self.bookmarks_menu.addAction("Manage Bookmarks", self.manage_bookmarks)
        self.bookmarks_menu.addSeparator()
        
        if not self.bookmarks:
            self.bookmarks_menu.addAction("No Bookmarks").setEnabled(False)
        else:
            for bm in self.bookmarks:
                action = self.bookmarks_menu.addAction(bm["name"])
                action.triggered.connect(lambda checked, url=bm["url"]: self.load_url(url))

    def update_history_menu(self):
        self.history_menu.clear()
        recent = self.history[-15:]
        if not recent:
            self.history_menu.addAction("No history recorded").setEnabled(False)
        else:
            for item in reversed(recent):
                action = self.history_menu.addAction(item.get("title", "") or item.get("url", ""))
                action.triggered.connect(lambda checked, url=item["url"]: self.load_url(url))
        self.history_menu.addSeparator()
        self.history_menu.addAction("Clear History", self.clear_history)

    def apply_global_settings(self):
        # Apply profile configuration settings globally
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(
            QWebEngineProfile.HttpCacheType.DiskHttpCache
            if self.settings.get("cache_enabled", True)
            else QWebEngineProfile.HttpCacheType.NoCache
        )
        
        # Configure WebEngine Settings via the default profile (PyQt6 API)
        s = profile.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, self.settings.get("javascript_enabled", True))
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, self.settings.get("local_storage_enabled", True))
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        
        # Apply style sheets
        self.setStyleSheet(self.get_stylesheet())
        
        # Set zoom on active tabs
        for i in range(self.tab_widget.count()):
            view = self.tab_widget.widget(i)
            if isinstance(view, QWebEngineView):
                view.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)


    def add_new_tab(self, url=None):
        if url is None:
            url = self.settings.get("home_page", "about:home")
            
        web_view = QWebEngineView()
        
        # Tab configuration
        page = RhodiumWebEnginePage(self, web_view)
        web_view.setPage(page)
        
        # Apply zoom
        web_view.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)
        
        # Signal Connections
        web_view.loadStarted.connect(lambda: self.on_load_started(web_view))
        web_view.loadProgress.connect(lambda p: self.on_load_progress(p, web_view))
        web_view.loadFinished.connect(lambda ok: self.on_load_finished(ok, web_view))
        web_view.titleChanged.connect(lambda t: self.on_title_changed(t, web_view))
        web_view.urlChanged.connect(lambda u: self.on_url_changed(u, web_view))
        
        # Downloads handler
        profile = page.profile()
        profile.downloadRequested.connect(self.on_download_requested)
        
        index = self.tab_widget.addTab(web_view, "Loading...")
        self.tab_widget.setCurrentIndex(index)
        
        if url == "about:home" or url == "rhodium://home":
            html = self.get_home_page_html()
            web_view.setHtml(html, QUrl("about:blank"))
        else:
            self.load_url_in_view(url, web_view)
            
        # Keyboard shortcut mapping for URL bar focus
        self.url_bar_shortcut = QAction(self)
        self.url_bar_shortcut.setShortcut(QKeySequence("Ctrl+L"))
        self.url_bar_shortcut.triggered.connect(self.url_bar.setFocus)
        self.addAction(self.url_bar_shortcut)
        
        return web_view

    def load_url_in_view(self, url_string, web_view):
        if not url_string.startswith(('http://', 'https://', 'file://', 'about:')):
            if '.' in url_string and ' ' not in url_string:
                url_string = 'https://' + url_string
            else:
                url_string = 'https://www.google.com/search?q=' + url_string.replace(' ', '+')
        web_view.load(QUrl(url_string))

    def navigate_to_url(self):
        url = self.url_bar.text()
        current_view = self.get_current_web_view()
        if current_view:
            if url == "about:home" or url == "rhodium://home":
                current_view.setHtml(self.get_home_page_html(), QUrl("about:blank"))
            else:
                self.load_url_in_view(url, current_view)

    def load_url(self, url):
        current_view = self.get_current_web_view()
        if current_view:
            if url == "about:home" or url == "rhodium://home":
                current_view.setHtml(self.get_home_page_html(), QUrl("about:blank"))
            else:
                self.load_url_in_view(url, current_view)

    def get_current_web_view(self):
        return self.tab_widget.currentWidget()

    def go_back(self):
        view = self.get_current_web_view()
        if view:
            view.back()

    def go_forward(self):
        view = self.get_current_web_view()
        if view:
            view.forward()

    def reload_page(self):
        view = self.get_current_web_view()
        if view:
            view.reload()

    def stop_loading(self):
        view = self.get_current_web_view()
        if view:
            view.stop()

    def go_home(self):
        self.load_url("about:home")

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            widget.deleteLater()
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def tab_changed(self, index):
        view = self.tab_widget.widget(index)
        if isinstance(view, QWebEngineView):
            url = view.url().toString()
            if url == "about:blank" or url == "":
                self.url_bar.setText("rhodium://home")
            else:
                self.url_bar.setText(url)
            self.update_bookmark_icon(url)

    def update_bookmark_icon(self, url):
        is_bookmarked = any(bm["url"] == url for bm in self.bookmarks)
        icon_name = "bookmark-check.png" if is_bookmarked else "bookmark.png"
        self.btn_bookmark.setIcon(QIcon(os.path.join("style", "icons", icon_name)))

    # Bookmarks
    def add_bookmark(self):
        view = self.get_current_web_view()
        if view:
            url = view.url().toString()
            title = view.title() or url
            if url == "about:blank" or url == "":
                url = "about:home"
                title = "RHODIUM Home"
                
            name, ok = QInputDialog.getText(self, "Add Bookmark", "Name:", text=title)
            if ok and name:
                if not any(bm["url"] == url for bm in self.bookmarks):
                    self.bookmarks.append({"name": name, "url": url})
                    self.save_bookmarks()
                    self.update_bookmarks_menu()
                    self.update_bookmark_icon(url)
                    self.status_label.setText(f"Bookmark added: {name}")

    def manage_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Bookmarks")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        list_widget = QListWidget()
        for idx, bm in enumerate(self.bookmarks):
            item = QListWidgetItem(f"{bm['name']} ({bm['url']})")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            list_widget.addItem(item)
            
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(os.path.join("style", "icons", "trash-2.png")))
        delete_btn.setToolTip("Delete selected")
        delete_btn.clicked.connect(lambda: self.delete_bookmark_from_list(list_widget, dialog))
        btn_layout.addWidget(delete_btn)
        
        open_btn = QPushButton("Open Bookmark")
        open_btn.clicked.connect(lambda: self.open_bookmark_from_list(list_widget, dialog))
        btn_layout.addWidget(open_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def delete_bookmark_from_list(self, list_widget, dialog):
        row = list_widget.currentRow()
        if row >= 0:
            self.bookmarks.pop(row)
            self.save_bookmarks()
            self.update_bookmarks_menu()
            dialog.accept()
            self.manage_bookmarks()

    def open_bookmark_from_list(self, list_widget, dialog):
        row = list_widget.currentRow()
        if row >= 0:
            url = self.bookmarks[row]["url"]
            self.load_url(url)
            dialog.accept()

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as f:
            json.dump(self.bookmarks, f, indent=2)

    def load_bookmarks(self):
        if self.bookmarks_file.exists():
            try:
                with open(self.bookmarks_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    # History
    def add_to_history(self, url, title):
        if not url or url.startswith("about:") or url.startswith("data:"):
            return
        if self.history and self.history[-1]["url"] == url:
            return
        self.history.append({
            "url": url,
            "title": title or url,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history()

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def clear_history(self):
        confirm = QMessageBox.question(self, "Clear History", "Are you sure you want to clear all history?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            self.status_label.setText("History cleared.")

    def clear_browsing_data_prompt(self):
        confirm = QMessageBox.question(self, "Clear Browsing Data", "Clear all browsing history, cache, and cached settings?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            QWebEngineProfile.defaultProfile().clearAllVisitedLinks()
            QWebEngineProfile.defaultProfile().clearHttpCache()
            QMessageBox.information(self, "Clear Data", "All browsing data cleared!")

    # Find In Page
    def open_find_dialog(self):
        self.find_bar.show()
        self.find_bar.search_input.setFocus()
        self.find_bar.search_input.selectAll()

    def perform_find(self, text, reverse=False):
        view = self.get_current_web_view()
        if view:
            options = QWebEnginePage.FindFlag(0)
            if reverse:
                options |= QWebEnginePage.FindFlag.FindBackward
            if self.find_bar.case_check.isChecked():
                options |= QWebEnginePage.FindFlag.FindCaseSensitively
            view.findText(text, options)

    # Zoom
    def zoom_in(self):
        view = self.get_current_web_view()
        if view:
            view.setZoomFactor(view.zoomFactor() + 0.1)

    def zoom_out(self):
        view = self.get_current_web_view()
        if view:
            view.setZoomFactor(max(0.2, view.zoomFactor() - 0.1))

    def reset_zoom(self):
        view = self.get_current_web_view()
        if view:
            view.setZoomFactor(1.0)

    # Full Screen
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # Settings
    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
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

    # Downloads
    def on_download_requested(self, download_item):
        dl_dir = self.settings.get("download_dir", str(Path.home() / "Downloads"))
        suggested_path = os.path.join(dl_dir, download_item.suggestedFileName())
        
        download_item.setDownloadDirectory(dl_dir)
        download_item.setDownloadFileName(download_item.suggestedFileName())
        download_item.accept()
        
        self.downloads.append({
            "name": download_item.suggestedFileName(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "path": suggested_path
        })
        self.save_downloads()
        self.status_label.setText(f"Downloading: {download_item.suggestedFileName()}")

    def load_downloads(self):
        if self.downloads_file.exists():
            try:
                with open(self.downloads_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_downloads(self):
        with open(self.downloads_file, "w") as f:
            json.dump(self.downloads, f, indent=2)

    def show_downloads(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Downloads Log")
        dialog.setMinimumSize(450, 300)
        
        layout = QVBoxLayout()
        list_widget = QListWidget()
        for dl in self.downloads:
            list_widget.addItem(f"{dl['name']} ({dl['date']}) - {dl['path']}")
            
        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.exec()

    # Signals / Web Engine Updates
    def on_load_started(self, web_view):
        if self.get_current_web_view() == web_view:
            self.status_label.setText("Loading...")

    def on_load_progress(self, progress, web_view):
        if self.get_current_web_view() == web_view:
            self.status_label.setText(f"Loading... {progress}%")

    def on_load_finished(self, ok, web_view):
        if self.get_current_web_view() == web_view:
            self.status_label.setText("Done" if ok else "Error loading page")
        url = web_view.url().toString()
        title = web_view.title() or url
        
        idx = self.tab_widget.indexOf(web_view)
        if idx >= 0:
            display_title = title if len(title) < 25 else title[:22] + "..."
            self.tab_widget.setTabText(idx, display_title)
            
        if self.get_current_web_view() == web_view:
            if url == "about:blank" or url == "":
                self.url_bar.setText("rhodium://home")
            else:
                self.url_bar.setText(url)
            self.update_bookmark_icon(url)
            
        if ok and url != "about:blank" and url != "":
            self.add_to_history(url, title)

    def on_title_changed(self, title, web_view):
        idx = self.tab_widget.indexOf(web_view)
        if idx >= 0:
            display_title = title if len(title) < 25 else title[:22] + "..."
            self.tab_widget.setTabText(idx, display_title)

    def on_url_changed(self, url, web_view):
        url_str = url.toString()
        if self.get_current_web_view() == web_view:
            if url_str == "about:blank" or url_str == "":
                self.url_bar.setText("rhodium://home")
            else:
                self.url_bar.setText(url_str)
            self.update_bookmark_icon(url_str)

    # General Handlers
    def open_new_window(self):
        new_window = AdvancedBrowser()
        new_window.show()

    def open_local_file(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "HTML Files (*.html *.htm);;All Files (*)")
        if file_path:
            self.load_url("file:///" + file_path.replace("\\", "/"))

    def open_dev_tools_info(self):
        QMessageBox.information(
            self, "Developer Tools", 
            "Developer Tools is a premium feature.\n"
            "To debug, you can set the environment variable QTWEBENGINE_REMOTE_DEBUGGING=port "
            "and inspect via localhost page in another tab."
        )

    def show_about(self):
        QMessageBox.about(self, "About RHODIUM",
                        "RHODIUM Browser\n\n"
                        "A professional, ultra-minimalistic web browser built using PyQt6 and QtWebEngine.\n"
                        "Designed with dark theme aesthetics.")

    def show_shortcuts(self):
        shortcuts_text = (
            "Ctrl+T : New Tab\n"
            "Ctrl+N : New Window\n"
            "Ctrl+W : Close Tab\n"
            "Ctrl+D : Add Bookmark\n"
            "Ctrl+F : Find in Page\n"
            "Ctrl+L : Focus URL Bar\n"
            "Ctrl+J : Show Downloads\n"
            "Ctrl++ : Zoom In\n"
            "Ctrl+- : Zoom Out\n"
            "Ctrl+0 : Reset Zoom\n"
            "F11 : Full Screen\n"
            "F5 : Reload\n"
            "Esc : Stop\n"
            "Alt+Left : Go Back\n"
            "Alt+Right : Go Forward"
        )
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setText(shortcuts_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec()

    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #0c0c0e;
            }
            QToolBar {
                background-color: #0f0f12;
                border-bottom: 1px solid #1a1a24;
                padding: 6px;
                spacing: 5px;
            }
            QPushButton {
                background-color: transparent;
                color: #d1d1db;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #24242e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #16161c;
                color: #eaeaea;
                border: 1px solid #282835;
                border-radius: 16px;
                padding: 6px 12px;
                font-size: 13px;
                margin-right: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #3c3c52;
                background-color: #1a1a22;
            }
            QTabWidget::pane {
                border: none;
                background-color: #050505;
            }
            QTabBar::tab {
                background-color: #0f0f12;
                color: #8c8c9e;
                border-bottom: 2px solid transparent;
                padding: 8px 16px;
                min-width: 120px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #050505;
                color: #ffffff;
                border-bottom: 2px solid #3066e3;
            }
            QTabBar::tab:hover {
                color: #d1d1db;
            }
            QStatusBar {
                background-color: #0f0f12;
                color: #717182;
                border-top: 1px solid #1a1a24;
            }
            QMenuBar {
                background-color: #0f0f12;
                color: #eaeaea;
                border-bottom: 1px solid #1a1a24;
            }
            QMenuBar::item:selected {
                background-color: #24242e;
            }
            QMenu {
                background-color: #16161c;
                color: #eaeaea;
                border: 1px solid #282835;
            }
            QMenu::item:selected {
                background-color: #3066e3;
                color: #ffffff;
            }
            QDialog {
                background-color: #0f0f12;
                color: #eaeaea;
            }
            QLabel {
                color: #eaeaea;
            }
            QCheckBox {
                color: #eaeaea;
            }
            #FindBar {
                background-color: #16161c;
                border-top: 1px solid #282835;
            }
        """

    def get_home_page_html(self):
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Rhodium Home</title>
            <style>
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                body {
                    background-color: #000000;
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    overflow: hidden;
                }
                .logo-container {
                    margin-bottom: 30px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .globe-logo {
                    width: 72px;
                    height: 72px;
                    background: radial-gradient(circle, #ffffff 40%, transparent 100%);
                    border-radius: 50%;
                    position: relative;
                    box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .globe-logo::before {
                    content: "🌐";
                    font-size: 42px;
                }
                .search-box {
                    position: relative;
                    width: 550px;
                    margin-bottom: 45px;
                }
                .search-box input {
                    width: 100%;
                    padding: 15px 50px;
                    background-color: #121212;
                    border: 1px solid #2b2b2b;
                    border-radius: 28px;
                    color: #ffffff;
                    font-size: 15px;
                    outline: none;
                    transition: border 0.3s, background-color 0.3s;
                }
                .search-box input:focus {
                    border-color: #4a4a4a;
                    background-color: #181818;
                }
                .search-box .search-icon {
                    position: absolute;
                    left: 18px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #888888;
                    font-size: 16px;
                }
                .search-box .mic-icon {
                    position: absolute;
                    right: 18px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #888888;
                    font-size: 16px;
                }
                .quick-links {
                    display: flex;
                    gap: 20px;
                }
                .link-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-decoration: none;
                    color: #a0a0a0;
                    font-size: 12px;
                    cursor: pointer;
                    transition: color 0.3s;
                }
                .link-item:hover {
                    color: #ffffff;
                }
                .link-box {
                    width: 54px;
                    height: 54px;
                    background-color: #121212;
                    border: 1px solid #232323;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 8px;
                    font-size: 20px;
                    color: #ffffff;
                    transition: background-color 0.3s, border-color 0.3s;
                }
                .link-item:hover .link-box {
                    background-color: #1c1c1c;
                    border-color: #3a3a3a;
                }
                .link-box.add-btn {
                    border-style: dashed;
                    color: #555555;
                }
                .link-item:hover .link-box.add-btn {
                    color: #a0a0a0;
                }
            </style>
        </head>
        <body>
            <div class="logo-container">
                <div class="globe-logo"></div>
            </div>
            
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="Search the web or type a URL" autofocus>
                <span class="mic-icon">🎤</span>
            </div>
            
            <div class="quick-links">
                <div class="link-item" onclick="navigate('https://mail.google.com')">
                    <div class="link-box">✉️</div>
                    <span>Mail</span>
                </div>
                <div class="link-item" onclick="navigate('https://youtube.com')">
                    <div class="link-box">▶️</div>
                    <span>Video</span>
                </div>
                <div class="link-item" onclick="navigate('https://github.com')">
                    <div class="link-box">&lt;&gt;</div>
                    <span>Dev</span>
                </div>
                <div class="link-item" onclick="navigate('https://news.google.com')">
                    <div class="link-box">📰</div>
                    <span>News</span>
                </div>
                <div class="link-item" onclick="navigate('https://twitter.com')">
                    <div class="link-box">💬</div>
                    <span>Social</span>
                </div>
                <div class="link-item" onclick="navigate('https://amazon.com')">
                    <div class="link-box">🛍️</div>
                    <span>Shop</span>
                </div>
                <div class="link-item" onclick="navigate('https://figma.com')">
                    <div class="link-box">🎨</div>
                    <span>Design</span>
                </div>
                <div class="link-item" onclick="addNewLink()">
                    <div class="link-box add-btn">+</div>
                    <span>Add</span>
                </div>
            </div>
            
            <script>
                const input = document.getElementById('searchInput');
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        let val = input.value.trim();
                        if (val) {
                            window.location.href = "rhodium://navigate?q=" + encodeURIComponent(val);
                        }
                    }
                });
                
                function navigate(url) {
                    window.location.href = "rhodium://navigate?q=" + encodeURIComponent(url);
                }
                
                function addNewLink() {
                    let name = prompt("Enter link name:");
                    let url = prompt("Enter link URL:");
                    if (name && url) {
                        window.location.href = "rhodium://navigate?q=" + encodeURIComponent(url);
                    }
                }
            </script>
        </body>
        </html>
        """


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RHODIUM Browser")
    app.setOrganizationName("Rhodium")
    window = AdvancedBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
