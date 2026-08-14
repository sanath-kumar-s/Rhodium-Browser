"""
Advanced Browser with PyQt6 and QtWebEngine
Features: Home page, toolbar, bookmarks, search, history, dark mode, and more
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QMenu,
    QInputDialog, QToolBar, QTabWidget, QStatusBar, QProgressBar,
    QMenuBar, QDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

class HomePage(QWidget):
    """Custom home page widget"""
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create HTML for home page
        html_content = self.get_home_page_html()
        
        self.web_view = QWebEngineView()
        self.web_view.setHtml(html_content, QUrl("about:blank"))
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def get_home_page_html(self):
        """Generate custom home page HTML"""
        bookmarks_html = self.get_bookmarks_html()
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Home</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    color: #fff;
                }}
                
                .container {{
                    width: 100%;
                    max-width: 1200px;
                    padding: 40px 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 60px;
                }}
                
                .logo {{
                    font-size: 48px;
                    font-weight: 700;
                    margin-bottom: 30px;
                    background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    letter-spacing: -1px;
                }}
                
                .search-container {{
                    margin-bottom: 50px;
                }}
                
                .search-box {{
                    width: 100%;
                    max-width: 600px;
                    padding: 16px 24px;
                    border: 2px solid #00d4ff;
                    border-radius: 50px;
                    background: rgba(0, 20, 40, 0.6);
                    color: #fff;
                    font-size: 16px;
                    transition: all 0.3s ease;
                    margin: 0 auto;
                    display: block;
                    backdrop-filter: blur(10px);
                }}
                
                .search-box:focus {{
                    outline: none;
                    background: rgba(0, 30, 60, 0.8);
                    box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
                    transform: translateY(-2px);
                }}
                
                .search-box::placeholder {{
                    color: rgba(255, 255, 255, 0.5);
                }}
                
                .quick-links {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 15px;
                    margin-bottom: 60px;
                    max-width: 600px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                
                .quick-link {{
                    padding: 12px 16px;
                    background: rgba(0, 212, 255, 0.1);
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    border-radius: 8px;
                    color: #00d4ff;
                    text-decoration: none;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 14px;
                    font-weight: 500;
                }}
                
                .quick-link:hover {{
                    background: rgba(0, 212, 255, 0.2);
                    border-color: rgba(0, 212, 255, 0.6);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
                }}
                
                .bookmarks-section {{
                    margin-top: 60px;
                    padding-top: 40px;
                    border-top: 1px solid rgba(0, 212, 255, 0.2);
                }}
                
                .section-title {{
                    font-size: 14px;
                    font-weight: 600;
                    color: rgba(0, 212, 255, 0.8);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 20px;
                }}
                
                .bookmarks-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                    gap: 12px;
                }}
                
                .bookmark {{
                    padding: 12px;
                    background: rgba(0, 212, 255, 0.05);
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    border-radius: 8px;
                    color: #fff;
                    text-decoration: none;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    word-break: break-word;
                    font-size: 13px;
                }}
                
                .bookmark:hover {{
                    background: rgba(0, 212, 255, 0.15);
                    border-color: rgba(0, 212, 255, 0.4);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.15);
                }}
                
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-top: 40px;
                    padding-top: 40px;
                    border-top: 1px solid rgba(0, 212, 255, 0.2);
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                
                .stat {{
                    text-align: center;
                }}
                
                .stat-number {{
                    font-size: 32px;
                    font-weight: 700;
                    color: #00d4ff;
                }}
                
                .stat-label {{
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.6);
                    margin-top: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🌐 RHODIUM</div>
                </div>
                
                <div class="search-container">
                    <input type="text" class="search-box" id="searchInput" placeholder="Search the web or type a URL...">
                </div>
                
                <div class="quick-links">
                    <a class="quick-link" onclick="navigate('https://www.google.com')">Google</a>
                    <a class="quick-link" onclick="navigate('https://www.wikipedia.org')">Wikipedia</a>
                    <a class="quick-link" onclick="navigate('https://www.github.com')">GitHub</a>
                    <a class="quick-link" onclick="navigate('https://www.stackoverflow.com')">Stack Overflow</a>
                    <a class="quick-link" onclick="navigate('https://www.youtube.com')">YouTube</a>
                </div>
                
                {bookmarks_html}
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">∞</div>
                        <div class="stat-label">Possibilities</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">⚡</div>
                        <div class="stat-label">Fast</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">🔒</div>
                        <div class="stat-label">Secure</div>
                    </div>
                </div>
            </div>
            
            <script>
                const searchInput = document.getElementById('searchInput');
                
                searchInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        const query = this.value.trim();
                        if (query) {{
                            navigate(query);
                        }}
                    }}
                }});
                
                function navigate(query) {{
                    if (query.startsWith('http://') || query.startsWith('https://')) {{
                        window.location.href = query;
                    }} else if (query.includes('.') && !query.includes(' ')) {{
                        window.location.href = 'https://' + query;
                    }} else {{
                        window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(query);
                    }}
                }}
                
                // Handle bookmark clicks
                document.querySelectorAll('.bookmark').forEach(el => {{
                    el.addEventListener('click', function() {{
                        const url = this.getAttribute('data-url');
                        if (url) navigate(url);
                    }});
                }});
                
                // Focus search on load
                searchInput.focus();
            </script>
        </body>
        </html>
        """

    def get_bookmarks_html(self):
        """Generate bookmarks HTML from saved bookmarks"""
        bookmarks = self.browser.load_bookmarks()
        
        if not bookmarks:
            return ""
        
        bookmarks_html = '<div class="bookmarks-section"><div class="section-title">📌 Bookmarks</div><div class="bookmarks-grid">'
        
        for bookmark in bookmarks:
            name = bookmark.get('name', 'Bookmark')[:15]
            url = bookmark.get('url', '#')
            bookmarks_html += f'<a class="bookmark" data-url="{url}" title="{name}">{name}</a>'
        
        bookmarks_html += '</div></div>'
        return bookmarks_html


class AdvancedBrowser(QMainWindow):
    """Main browser window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RHODIUM - Advanced Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data paths
        self.config_dir = Path.home() / ".rhodium"
        self.config_dir.mkdir(exist_ok=True)
        self.bookmarks_file = self.config_dir / "bookmarks.json"
        self.history_file = self.config_dir / "history.json"
        
        # Initialize browser data
        self.bookmarks = self.load_bookmarks()
        self.history = self.load_history()
        
        # Create UI
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
        
    def init_ui(self):
        """Initialize UI components"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.toolbar = self.create_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Create tab widget for multiple tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget)
        
        # Add first tab
        self.add_new_tab()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.statusBar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_toolbar(self):
        """Create the toolbar with navigation buttons"""
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QIcon().actualSize(toolbar.iconSize()))
        toolbar.setObjectName("NavigationToolbar")
        
        # Back button
        self.back_btn = QPushButton("◄")
        self.back_btn.setToolTip("Go Back")
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        # Forward button
        self.forward_btn = QPushButton("►")
        self.forward_btn.setToolTip("Go Forward")
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        # Reload button
        self.reload_btn = QPushButton("⟳")
        self.reload_btn.setToolTip("Reload Page (F5)")
        self.reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(self.reload_btn)
        
        # Home button
        self.home_btn = QPushButton("⌂")
        self.home_btn.setToolTip("Go Home")
        self.home_btn.clicked.connect(self.go_home)
        toolbar.addWidget(self.home_btn)
        
        toolbar.addSeparator()
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        toolbar.addSeparator()
        
        # New Tab button
        new_tab_btn = QPushButton("+ Tab")
        new_tab_btn.setToolTip("New Tab (Ctrl+T)")
        new_tab_btn.clicked.connect(self.add_new_tab)
        toolbar.addWidget(new_tab_btn)
        
        # Bookmark button
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setToolTip("Add Bookmark (Ctrl+D)")
        self.bookmark_btn.clicked.connect(self.add_bookmark)
        toolbar.addWidget(self.bookmark_btn)
        
        # History button
        history_btn = QPushButton("⌚")
        history_btn.setToolTip("View History")
        history_btn.setMenu(self.create_history_menu())
        toolbar.addWidget(history_btn)
        
        return toolbar
        
    def create_history_menu(self):
        """Create history dropdown menu"""
        menu = QMenu()
        
        recent_history = self.history[-10:] if len(self.history) > 10 else self.history
        
        for item in reversed(recent_history):
            action = menu.addAction(f"{item.get('title', 'No Title')} - {item.get('url', '')[:50]}")
            action.triggered.connect(lambda checked, url=item['url']: self.load_url(url))
        
        menu.addSeparator()
        clear_action = menu.addAction("Clear History")
        clear_action.triggered.connect(self.clear_history)
        
        return menu
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Tab", self.add_new_tab).setShortcut("Ctrl+T")
        file_menu.addAction("New Window", self.open_new_window).setShortcut("Ctrl+N")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close).setShortcut("Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Find", self.open_find_dialog).setShortcut("Ctrl+F")
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Zoom In", self.zoom_in).setShortcut("Ctrl++")
        view_menu.addAction("Zoom Out", self.zoom_out).setShortcut("Ctrl+-")
        view_menu.addAction("Reset Zoom", self.reset_zoom).setShortcut("Ctrl+0")
        view_menu.addSeparator()
        view_menu.addAction("Full Screen", self.toggle_fullscreen).setShortcut("F11")
        
        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")
        bookmarks_menu.addAction("Add Bookmark", self.add_bookmark).setShortcut("Ctrl+D")
        bookmarks_menu.addAction("Manage Bookmarks", self.manage_bookmarks)
        bookmarks_menu.addSeparator()
        
        for bookmark in self.bookmarks:
            action = bookmarks_menu.addAction(bookmark['name'])
            action.triggered.connect(lambda checked, url=bookmark['url']: self.load_url(url))
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Developer Tools", self.open_developer_tools).setShortcut("F12")
        tools_menu.addAction("Settings", self.open_settings)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        
    def add_new_tab(self, url="about:home"):
        """Add a new browser tab"""
        web_view = QWebEngineView()
        
        # Create web page with custom settings
        page = QWebEnginePage()
        
        # Configure settings
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
        web_view.setPage(page)
        
        # Connect signals
        web_view.loadStarted.connect(lambda: self.on_load_started(web_view))
        web_view.loadProgress.connect(lambda progress: self.on_load_progress(progress))
        web_view.loadFinished.connect(lambda: self.on_load_finished(web_view))
        web_view.titleChanged.connect(lambda title: self.on_title_changed(web_view, title))
        web_view.urlChanged.connect(lambda url: self.on_url_changed(web_view, url))
        
        # Handle custom protocols
        web_view.page().acceptNavigationRequest = self.handle_navigation
        
        # Load home page or URL
        if url == "about:home":
            home_page = HomePage(self)
            web_view.setHtml(home_page.get_home_page_html(), QUrl("about:blank"))
        else:
            web_view.load(QUrl(url))
        
        # Add tab
        index = self.tab_widget.addTab(web_view, "Loading...")
        self.tab_widget.setCurrentIndex(index)
        
        return web_view
        
    def get_current_web_view(self):
        """Get the current active web view"""
        return self.tab_widget.currentWidget()
        
    def load_url(self, url_string):
        """Load a URL in the current tab"""
        if not url_string.startswith(('http://', 'https://')):
            if '.' in url_string and ' ' not in url_string:
                url_string = 'https://' + url_string
            else:
                url_string = 'https://www.google.com/search?q=' + url_string.replace(' ', '+')
        
        web_view = self.get_current_web_view()
        web_view.load(QUrl(url_string))
        
    def navigate_to_url(self):
        """Navigate to URL from the URL bar"""
        url = self.url_bar.text()
        self.load_url(url)
        
    def go_back(self):
        """Go back"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.back()
            
    def go_forward(self):
        """Go forward"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.forward()
            
    def reload_page(self):
        """Reload current page"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.reload()
            
    def go_home(self):
        """Go to home page"""
        web_view = self.get_current_web_view()
        if web_view:
            home_page = HomePage(self)
            web_view.setHtml(home_page.get_home_page_html(), QUrl("about:blank"))
            self.url_bar.setText("about:home")
            
    def add_bookmark(self):
        """Add current page to bookmarks"""
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            title = web_view.title()
            
            if not url or url == "about:blank":
                QMessageBox.warning(self, "Error", "Cannot bookmark this page")
                return
            
            name, ok = QInputDialog.getText(self, "Add Bookmark", 
                                          "Bookmark Name:", text=title)
            
            if ok and name:
                bookmark = {"name": name, "url": url}
                if bookmark not in self.bookmarks:
                    self.bookmarks.append(bookmark)
                    self.save_bookmarks()
                    QMessageBox.information(self, "Success", "Bookmark added!")
                    
                    # Update menu bar bookmarks
                    self.create_menu_bar()
                    
    def manage_bookmarks(self):
        """Manage bookmarks"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Bookmarks")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        label = QLabel("Your Bookmarks:")
        layout.addWidget(label)
        
        # Display bookmarks
        for i, bookmark in enumerate(self.bookmarks):
            btn_layout = QHBoxLayout()
            label = QLabel(f"{bookmark['name']} - {bookmark['url'][:30]}...")
            btn_layout.addWidget(label)
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_bookmark(idx))
            btn_layout.addWidget(delete_btn)
            
            layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
        
    def delete_bookmark(self, index):
        """Delete a bookmark"""
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.save_bookmarks()
            QMessageBox.information(self, "Success", "Bookmark deleted!")
            
    def open_find_dialog(self):
        """Open find dialog"""
        text, ok = QInputDialog.getText(self, "Find", "Find in page:")
        if ok and text:
            web_view = self.get_current_web_view()
            if web_view:
                web_view.findText(text)
                
    def zoom_in(self):
        """Increase page zoom"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() + 0.1)
            
    def zoom_out(self):
        """Decrease page zoom"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() - 0.1)
            
    def reset_zoom(self):
        """Reset page zoom"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def open_new_window(self):
        """Open a new browser window"""
        new_browser = AdvancedBrowser()
        new_browser.show()
        
    def open_developer_tools(self):
        """Open developer tools"""
        QMessageBox.information(self, "Developer Tools", 
                              "Developer tools can be opened by pressing F12 in your browser.\n"
                              "PyQt6 WebEngine has limited built-in dev tools support.\n"
                              "Consider using web-based debugging instead.")
        
    def open_settings(self):
        """Open settings dialog"""
        QMessageBox.information(self, "Settings", 
                              "Settings panel coming soon!\n\n"
                              "Current features:\n"
                              "- Multiple tabs\n"
                              "- Bookmarks management\n"
                              "- Browser history\n"
                              "- Zoom controls")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About RHODIUM",
                        "RHODIUM - Advanced Web Browser\n\n"
                        "A modern browser built with PyQt6 and QtWebEngine\n\n"
                        "Features:\n"
                        "✓ Tabbed browsing\n"
                        "✓ Bookmarks management\n"
                        "✓ History tracking\n"
                        "✓ Zoom controls\n"
                        "✓ Custom home page\n"
                        "✓ Search functionality\n\n"
                        "Version 1.0")
        
    def close_tab(self, index):
        """Close a tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()
            
    def on_load_started(self, web_view):
        """Called when page loading starts"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
    def on_load_progress(self, progress):
        """Called during page loading"""
        self.progress_bar.setValue(progress)
        
    def on_load_finished(self, web_view):
        """Called when page loading finishes"""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(100)
        
    def on_title_changed(self, web_view, title):
        """Called when page title changes"""
        index = self.tab_widget.indexOf(web_view)
        if index >= 0:
            self.tab_widget.setTabText(index, title[:20] + "..." if len(title) > 20 else title)
            
    def on_url_changed(self, web_view, url):
        """Called when URL changes"""
        if self.get_current_web_view() == web_view:
            self.url_bar.setText(url.toString())
        
        # Add to history
        self.add_to_history(url.toString(), web_view.title())
        
    def handle_navigation(self, navigation_request):
        """Handle navigation requests"""
        return True
        
    def add_to_history(self, url, title):
        """Add URL to history"""
        if url and not url.startswith("about:"):
            self.history.append({
                "url": url,
                "title": title,
                "timestamp": datetime.now().isoformat()
            })
            self.save_history()
            
    def clear_history(self):
        """Clear browsing history"""
        reply = QMessageBox.question(self, "Clear History", 
                                    "Are you sure you want to clear all history?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history = []
            self.save_history()
            QMessageBox.information(self, "Success", "History cleared!")
            
    def save_bookmarks(self):
        """Save bookmarks to file"""
        with open(self.bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f, indent=2)
            
    def load_bookmarks(self):
        """Load bookmarks from file"""
        if self.bookmarks_file.exists():
            with open(self.bookmarks_file, 'r') as f:
                return json.load(f)
        return []
        
    def save_history(self):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def load_history(self):
        """Load history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
        
    def get_stylesheet(self):
        """Get application stylesheet"""
        return """
            QMainWindow {
                background-color: #1a1a2e;
            }
            
            QToolBar {
                background-color: #16213e;
                border-bottom: 1px solid #0f3460;
                padding: 4px;
                spacing: 4px;
            }
            
            QPushButton {
                background-color: #0f3460;
                color: #00d4ff;
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #00d4ff;
                color: #16213e;
            }
            
            QPushButton:pressed {
                background-color: #009acc;
            }
            
            QLineEdit {
                background-color: #0f3460;
                color: #fff;
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 6px 8px;
                selection-background-color: #00d4ff;
            }
            
            QLineEdit:focus {
                border: 2px solid #00d4ff;
            }
            
            QTabWidget {
                background-color: #1a1a2e;
            }
            
            QTabBar::tab {
                background-color: #0f3460;
                color: #fff;
                padding: 6px 12px;
                border: 1px solid #00d4ff;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #00d4ff;
                color: #16213e;
            }
            
            QStatusBar {
                background-color: #16213e;
                color: #fff;
                border-top: 1px solid #0f3460;
            }
            
            QMenuBar {
                background-color: #16213e;
                color: #fff;
                border-bottom: 1px solid #0f3460;
            }
            
            QMenuBar::item:selected {
                background-color: #0f3460;
            }
            
            QMenu {
                background-color: #16213e;
                color: #fff;
                border: 1px solid #0f3460;
            }
            
            QMenu::item:selected {
                background-color: #00d4ff;
                color: #16213e;
            }
            
            QProgressBar {
                background-color: #0f3460;
                border: 1px solid #00d4ff;
                border-radius: 2px;
                text-align: center;
                color: #00d4ff;
            }
            
            QProgressBar::chunk {
                background-color: #00d4ff;
            }
        """


def main():
    app = QApplication(sys.argv)
    browser = AdvancedBrowser()
    browser.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
