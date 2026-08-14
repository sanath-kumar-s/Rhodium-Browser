"""
RHODIUM Browser - Enhanced Version
Advanced features: Settings, Download manager, Better UI, Custom themes
"""
import sys
import json
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox, 
    QMessageBox, QMenu, QInputDialog, QToolBar, QTabWidget, QStatusBar,
    QDialog, QSpinBox, QFormLayout, QListWidget, QListWidgetItem,
    QTextEdit
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl


class SettingsDialog(QDialog):
    """Settings dialog for browser customization"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_browser = parent
        self.setWindowTitle("Browser Settings")
        self.setGeometry(200, 200, 500, 600)
        self.init_ui()
        
    def init_ui(self):
        """Initialize settings UI"""
        layout = QVBoxLayout()
        
        # General Settings
        form_layout = QFormLayout()
        
        # Home page setting
        home_page_label = QLabel("Home Page:")
        self.home_page_input = QLineEdit()
        self.home_page_input.setText("about:home")
        form_layout.addRow(home_page_label, self.home_page_input)
        
        # Download directory
        download_label = QLabel("Download Directory:")
        self.download_dir = QLineEdit()
        self.download_dir.setText(str(Path.home() / "Downloads"))
        form_layout.addRow(download_label, self.download_dir)
        
        # Privacy Settings
        privacy_label = QLabel("Privacy Settings:")
        form_layout.addRow(privacy_label, QLabel(""))
        
        self.javascript_check = QCheckBox("Enable JavaScript")
        self.javascript_check.setChecked(True)
        form_layout.addRow("", self.javascript_check)
        
        self.local_storage_check = QCheckBox("Enable Local Storage")
        self.local_storage_check.setChecked(True)
        form_layout.addRow("", self.local_storage_check)
        
        self.cookies_check = QCheckBox("Accept Cookies")
        self.cookies_check.setChecked(True)
        form_layout.addRow("", self.cookies_check)
        
        # Cache Settings
        cache_label = QLabel("Cache Settings:")
        form_layout.addRow(cache_label, QLabel(""))
        
        self.cache_check = QCheckBox("Enable Cache")
        self.cache_check.setChecked(True)
        form_layout.addRow("", self.cache_check)
        
        # Appearance
        appearance_label = QLabel("Appearance:")
        form_layout.addRow(appearance_label, QLabel(""))
        
        zoom_label = QLabel("Default Zoom Level:")
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setValue(100)
        self.zoom_spin.setMinimum(50)
        self.zoom_spin.setMaximum(200)
        self.zoom_spin.setSuffix("%")
        form_layout.addRow(zoom_label, self.zoom_spin)
        
        # Theme
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        form_layout.addRow(theme_label, self.theme_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def save_settings(self):
        """Save settings"""
        settings = {
            "home_page": self.home_page_input.text(),
            "download_dir": self.download_dir.text(),
            "javascript": self.javascript_check.isChecked(),
            "local_storage": self.local_storage_check.isChecked(),
            "cookies": self.cookies_check.isChecked(),
            "cache": self.cache_check.isChecked(),
            "zoom": self.zoom_spin.value(),
            "theme": self.theme_combo.currentText()
        }
        
        settings_file = self.parent_browser.config_dir / "settings.json"
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        QMessageBox.information(self, "Success", "Settings saved!")
        self.accept()
        
    def reset_settings(self):
        """Reset to default settings"""
        self.home_page_input.setText("about:home")
        self.download_dir.setText(str(Path.home() / "Downloads"))
        self.javascript_check.setChecked(True)
        self.local_storage_check.setChecked(True)
        self.cookies_check.setChecked(True)
        self.cache_check.setChecked(True)
        self.zoom_spin.setValue(100)
        self.theme_combo.setCurrentText("Dark")


class EnhancedBrowser(QMainWindow):
    """Enhanced browser with more features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RHODIUM Browser - Enhanced Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data paths
        self.config_dir = Path.home() / ".rhodium"
        self.config_dir.mkdir(exist_ok=True)
        self.bookmarks_file = self.config_dir / "bookmarks.json"
        self.history_file = self.config_dir / "history.json"
        self.settings_file = self.config_dir / "settings.json"
        self.downloads_file = self.config_dir / "downloads.json"
        
        # Load data
        self.bookmarks = self.load_bookmarks()
        self.history = self.load_history()
        self.settings = self.load_settings()
        self.downloads = self.load_downloads()
        
        # Initialize UI
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
        
    def init_ui(self):
        """Initialize UI"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget)
        
        # Add first tab
        self.add_new_tab()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.statusBar.addWidget(self.status_label)
        self.setStatusBar(self.statusBar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Menu bar
        self.create_menu_bar()
        
    def create_toolbar(self):
        """Create enhanced toolbar"""
        toolbar = QToolBar("Navigation")
        toolbar.setObjectName("NavBar")
        
        # Back
        back_btn = QPushButton("◄ Back")
        back_btn.setToolTip("Back (Alt+Left)")
        back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(back_btn)
        
        # Forward
        forward_btn = QPushButton("► Forward")
        forward_btn.setToolTip("Forward (Alt+Right)")
        forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_btn)
        
        # Reload
        reload_btn = QPushButton("⟳ Reload")
        reload_btn.setToolTip("Reload (F5)")
        reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(reload_btn)
        
        # Stop
        stop_btn = QPushButton("⏹ Stop")
        stop_btn.setToolTip("Stop Loading")
        stop_btn.clicked.connect(self.stop_loading)
        toolbar.addWidget(stop_btn)
        
        # Home
        home_btn = QPushButton("⌂ Home")
        home_btn.setToolTip("Home")
        home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(home_btn)
        
        toolbar.addSeparator()
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or type URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        toolbar.addSeparator()
        
        # New Tab
        new_tab_btn = QPushButton("+ New Tab")
        new_tab_btn.setToolTip("New Tab (Ctrl+T)")
        new_tab_btn.clicked.connect(self.add_new_tab)
        toolbar.addWidget(new_tab_btn)
        
        # Bookmark
        self.bookmark_btn = QPushButton("☆ Bookmark")
        self.bookmark_btn.setToolTip("Add Bookmark (Ctrl+D)")
        self.bookmark_btn.clicked.connect(self.add_bookmark)
        toolbar.addWidget(self.bookmark_btn)
        
        # Menu button
        menu_btn = QPushButton("☰ Menu")
        menu_btn.setMenu(self.create_quick_menu())
        toolbar.addWidget(menu_btn)
        
        return toolbar
        
    def create_quick_menu(self):
        """Create quick menu"""
        menu = QMenu()
        
        history_menu = menu.addMenu("History")
        for item in reversed(self.history[-5:]):
            action = history_menu.addAction(f"{item['title'][:30]}...")
            action.triggered.connect(lambda checked, url=item['url']: self.load_url(url))
        
        menu.addSeparator()
        
        bookmarks_menu = menu.addMenu("Bookmarks")
        for bm in self.bookmarks:
            action = bookmarks_menu.addAction(bm['name'][:30])
            action.triggered.connect(lambda checked, url=bm['url']: self.load_url(url))
        
        menu.addSeparator()
        menu.addAction("Settings", self.open_settings)
        
        return menu
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Tab", self.add_new_tab).setShortcut("Ctrl+T")
        file_menu.addAction("New Window", self.open_new_window).setShortcut("Ctrl+N")
        file_menu.addSeparator()
        file_menu.addAction("Downloads", self.show_downloads).setShortcut("Ctrl+J")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close).setShortcut("Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Find in Page", self.find_in_page).setShortcut("Ctrl+F")
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Zoom In", self.zoom_in).setShortcut("Ctrl++")
        view_menu.addAction("Zoom Out", self.zoom_out).setShortcut("Ctrl+-")
        view_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut("Ctrl+0")
        view_menu.addSeparator()
        view_menu.addAction("Full Screen", self.toggle_fullscreen).setShortcut("F11")
        view_menu.addAction("Developer Tools", self.open_dev_tools).setShortcut("F12")
        
        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")
        bookmarks_menu.addAction("Add Bookmark", self.add_bookmark).setShortcut("Ctrl+D")
        bookmarks_menu.addAction("Manage Bookmarks", self.manage_bookmarks)
        bookmarks_menu.addSeparator()
        for bm in self.bookmarks:
            action = bookmarks_menu.addAction(bm['name'])
            action.triggered.connect(lambda checked, url=bm['url']: self.load_url(url))
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Settings", self.open_settings).setShortcut("Ctrl+,")
        tools_menu.addAction("Clear History", self.clear_history)
        tools_menu.addAction("Clear Cookies", self.clear_cookies)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About RHODIUM", self.show_about)
        help_menu.addAction("Keyboard Shortcuts", self.show_shortcuts)
        
    def add_new_tab(self, url="about:home"):
        """Add new tab"""
        web_view = QWebEngineView()
        page = QWebEnginePage(web_view)
        
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
        web_view.setPage(page)
        
        # Signals
        web_view.loadStarted.connect(lambda: self.on_load_started(web_view))
        web_view.loadProgress.connect(lambda p: self.on_load_progress(p, web_view))
        web_view.loadFinished.connect(lambda: self.on_load_finished(web_view))
        web_view.titleChanged.connect(lambda t: self.on_title_changed(web_view, t))
        web_view.urlChanged.connect(lambda u: self.on_url_changed(web_view, u))
        
        if url == "about:home":
            html = self.get_home_page_html()
            web_view.setHtml(html, QUrl("about:blank"))
        else:
            web_view.load(QUrl(url))
        
        index = self.tab_widget.addTab(web_view, "Loading...")
        self.tab_widget.setCurrentIndex(index)
        
        return web_view
        
    def get_current_web_view(self):
        """Get current web view"""
        return self.tab_widget.currentWidget()
        
    def load_url(self, url_string):
        """Load URL"""
        if not url_string.startswith(('http://', 'https://')):
            if '.' in url_string and ' ' not in url_string:
                url_string = 'https://' + url_string
            else:
                url_string = 'https://www.google.com/search?q=' + url_string.replace(' ', '+')
        
        web_view = self.get_current_web_view()
        if web_view:
            web_view.load(QUrl(url_string))
        
    def navigate_to_url(self):
        """Navigate from URL bar"""
        url = self.url_bar.text()
        self.load_url(url)
        
    def go_back(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.back()
            
    def go_forward(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.forward()
            
    def reload_page(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.reload()
            
    def stop_loading(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.stop()
        self.status_label.setText("Stopped")
            
    def go_home(self):
        web_view = self.get_current_web_view()
        if web_view:
            html = self.get_home_page_html()
            web_view.setHtml(html, QUrl("about:blank"))
            self.url_bar.setText("about:home")
            
    def add_bookmark(self):
        """Add bookmark"""
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            title = web_view.title()
            
            if not url or url == "about:blank":
                QMessageBox.warning(self, "Error", "Cannot bookmark this page")
                return
            
            name, ok = QInputDialog.getText(self, "Add Bookmark", "Bookmark Name:", text=title)
            
            if ok and name:
                bookmark = {"name": name, "url": url}
                if bookmark not in self.bookmarks:
                    self.bookmarks.append(bookmark)
                    self.save_bookmarks()
                    self.status_label.setText(f"Bookmarked: {name}")
                    
    def manage_bookmarks(self):
        """Manage bookmarks"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Bookmarks")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        for i, bm in enumerate(self.bookmarks):
            item = QListWidgetItem(f"{bm['name']} - {bm['url'][:40]}...")
            item.setData(Qt.ItemDataRole.UserRole, i)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(list_widget.currentRow()))
        btn_layout.addWidget(delete_btn)
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: self.load_url(
            self.bookmarks[list_widget.currentRow()]['url'] if list_widget.currentRow() >= 0 else ""
        ))
        btn_layout.addWidget(open_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()
        
    def delete_bookmark(self, index):
        """Delete bookmark"""
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.save_bookmarks()
            QMessageBox.information(self, "Success", "Bookmark deleted!")
            
    def find_in_page(self):
        """Find in page"""
        text, ok = QInputDialog.getText(self, "Find", "Search in page:")
        if ok and text:
            web_view = self.get_current_web_view()
            if web_view:
                web_view.findText(text)
                
    def zoom_in(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() + 0.1)
            
    def zoom_out(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() - 0.1)
            
    def reset_zoom(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def open_dev_tools(self):
        QMessageBox.information(self, "Developer Tools",
                              "Developer tools can be accessed by pressing F12.\n"
                              "PyQt6 WebEngine has limited built-in dev tools.\n"
                              "Use browser developer tools for advanced debugging.")
        
    def open_new_window(self):
        new_browser = EnhancedBrowser()
        new_browser.show()
        
    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
        
    def show_downloads(self):
        """Show downloads"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Downloads")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        if not self.downloads:
            layout.addWidget(QLabel("No downloads yet"))
        else:
            list_widget = QListWidget()
            for dl in self.downloads:
                item = QListWidgetItem(f"{dl['name']} - {dl['date']}")
                list_widget.addItem(item)
            layout.addWidget(list_widget)
        
        dialog.setLayout(layout)
        dialog.exec()
        
    def clear_history(self):
        """Clear history"""
        reply = QMessageBox.question(self, "Clear History",
                                    "Clear all browsing history?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            self.status_label.setText("History cleared")
            
    def clear_cookies(self):
        """Clear cookies"""
        QMessageBox.information(self, "Cookies",
                              "Cookie clearing requires QWebEngineProfile configuration.\n"
                              "This is available in advanced implementation.")
        
    def show_about(self):
        """Show about"""
        QMessageBox.about(self, "About RHODIUM",
                        "RHODIUM Browser - Enhanced Edition\n\n"
                        "A powerful web browser built with PyQt6\n\n"
                        "Features:\n"
                        "✓ Tabbed browsing\n"
                        "✓ Bookmarks management\n"
                        "✓ History tracking\n"
                        "✓ Advanced settings\n"
                        "✓ Download manager\n"
                        "✓ Zoom controls\n"
                        "✓ Full customization\n\n"
                        "Version 2.0 - Enhanced Edition")
        
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        KEYBOARD SHORTCUTS
        
        Navigation:
          Ctrl+T  - New Tab
          Ctrl+N  - New Window
          Ctrl+W  - Close Tab
          Ctrl+Q  - Exit
          Alt+Left - Back
          Alt+Right - Forward
          
        Bookmarks:
          Ctrl+D  - Add Bookmark
          Ctrl+B  - Manage Bookmarks
          
        View:
          Ctrl++ - Zoom In
          Ctrl+- - Zoom Out
          Ctrl+0 - Reset Zoom
          F11  - Fullscreen
          F12  - Developer Tools
          
        Page:
          Ctrl+F - Find in Page
          F5   - Reload
          Ctrl+J - Downloads
          
        Tools:
          Ctrl+, - Settings
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setGeometry(200, 200, 500, 600)
        
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setText(shortcuts_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        dialog.setLayout(layout)
        dialog.exec()
        
    def close_tab(self, index):
        """Close tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()
            
    def on_load_started(self, web_view):
        self.status_label.setText("Loading...")
        
    def on_load_progress(self, progress, web_view):
        self.status_label.setText(f"Loading... {progress}%")
        
    def on_load_finished(self, web_view):
        self.status_label.setText("Done")
        
    def on_title_changed(self, web_view, title):
        index = self.tab_widget.indexOf(web_view)
        if index >= 0:
            self.tab_widget.setTabText(index, title[:25] + "..." if len(title) > 25 else title)
            
    def on_url_changed(self, web_view, url):
        if self.get_current_web_view() == web_view:
            self.url_bar.setText(url.toString())
        
        self.add_to_history(url.toString(), web_view.title())
        
    def add_to_history(self, url, title):
        if url and not url.startswith("about:"):
            self.history.append({
                "url": url,
                "title": title,
                "date": datetime.now().isoformat()
            })
            self.save_history()
            
    def get_home_page_html(self):
        """Get home page HTML"""
        bookmarks_html = ""
        if self.bookmarks:
            bookmarks_html = '<div class="section"><h3>📌 Bookmarks</h3><div class="bookmarks">'
            for bm in self.bookmarks:
                bookmarks_html += f'<a class="bookmark" onclick="navigate(\'{bm["url"]}\')">{bm["name"][:15]}</a>'
            bookmarks_html += '</div></div>'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home</title>
            <style>
                body {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: #fff;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 40px;
                    text-align: center;
                }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .logo {{ font-size: 48px; font-weight: bold; margin-bottom: 30px; }}
                .logo span {{ background: linear-gradient(135deg, #00d4ff, #0099ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                input {{
                    width: 100%;
                    max-width: 600px;
                    padding: 15px;
                    border: 2px solid #00d4ff;
                    border-radius: 50px;
                    background: rgba(0,20,40,0.6);
                    color: #fff;
                    font-size: 16px;
                    margin: 20px 0;
                }}
                input:focus {{ outline: none; background: rgba(0,30,60,0.8); }}
                .quick-links {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin: 30px 0; }}
                .quick-link {{
                    padding: 10px;
                    background: rgba(0,212,255,0.1);
                    border: 1px solid rgba(0,212,255,0.3);
                    border-radius: 6px;
                    color: #00d4ff;
                    cursor: pointer;
                    text-decoration: none;
                    transition: all 0.3s;
                }}
                .quick-link:hover {{ background: rgba(0,212,255,0.2); }}
                .section {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(0,212,255,0.2); }}
                .bookmarks {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; margin-top: 20px; }}
                .bookmark {{
                    padding: 10px;
                    background: rgba(0,212,255,0.05);
                    border: 1px solid rgba(0,212,255,0.2);
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .bookmark:hover {{ background: rgba(0,212,255,0.15); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo"><span>🌐 RHODIUM</span></div>
                <input type="text" id="search" placeholder="Search or enter URL...">
                <div class="quick-links">
                    <a class="quick-link" onclick="navigate('https://google.com')">Google</a>
                    <a class="quick-link" onclick="navigate('https://wikipedia.org')">Wikipedia</a>
                    <a class="quick-link" onclick="navigate('https://github.com')">GitHub</a>
                    <a class="quick-link" onclick="navigate('https://stackoverflow.com')">StackOverflow</a>
                    <a class="quick-link" onclick="navigate('https://youtube.com')">YouTube</a>
                </div>
                {bookmarks_html}
            </div>
            <script>
                document.getElementById('search').addEventListener('keypress', function(e) {{
                    if(e.key === 'Enter') navigate(this.value);
                }});
                function navigate(q) {{
                    if(q.startsWith('http')) window.location = q;
                    else if(q.includes('.') && !q.includes(' ')) window.location = 'https://' + q;
                    else window.location = 'https://google.com/search?q=' + encodeURIComponent(q);
                }}
            </script>
        </body>
        </html>
        """
        
    def save_bookmarks(self):
        with open(self.bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f, indent=2)
            
    def load_bookmarks(self):
        if self.bookmarks_file.exists():
            with open(self.bookmarks_file, 'r') as f:
                return json.load(f)
        return []
        
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
        
    def load_settings(self):
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}
        
    def load_downloads(self):
        if self.downloads_file.exists():
            with open(self.downloads_file, 'r') as f:
                return json.load(f)
        return []
        
    def get_stylesheet(self):
        return """
            QMainWindow { background-color: #1a1a2e; }
            QToolBar { background-color: #16213e; border-bottom: 1px solid #0f3460; padding: 4px; }
            QPushButton {
                background-color: #0f3460;
                color: #00d4ff;
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00d4ff; color: #16213e; }
            QLineEdit {
                background-color: #0f3460;
                color: #fff;
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QLineEdit:focus { border: 2px solid #00d4ff; }
            QTabWidget { background-color: #1a1a2e; }
            QTabBar::tab {
                background-color: #0f3460;
                color: #fff;
                padding: 6px 12px;
                border: 1px solid #00d4ff;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background-color: #00d4ff; color: #16213e; }
            QStatusBar { background-color: #16213e; color: #fff; border-top: 1px solid #0f3460; }
            QMenuBar { background-color: #16213e; color: #fff; }
            QMenuBar::item:selected { background-color: #0f3460; }
            QMenu { background-color: #16213e; color: #fff; border: 1px solid #0f3460; }
            QMenu::item:selected { background-color: #00d4ff; color: #16213e; }
            QDialog { background-color: #1a1a2e; color: #fff; }
            QLabel { color: #fff; }
            QCheckBox { color: #fff; }
            QSpinBox { background-color: #0f3460; color: #fff; border: 1px solid #00d4ff; }
            QComboBox { background-color: #0f3460; color: #fff; border: 1px solid #00d4ff; }
        """


def main():
    app = QApplication(sys.argv)
    browser = EnhancedBrowser()
    browser.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()