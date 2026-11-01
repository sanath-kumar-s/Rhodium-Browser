import ctypes
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QCheckBox, QSpinBox, QComboBox, QHBoxLayout, QPushButton,
    QMessageBox, QFileDialog, QWidget
)
from PyQt6.QtCore import Qt
from rhodium.utils import icon

class SettingsDialog(QDialog):
    """Settings dialog for browser configuration"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_browser = parent
        self.setWindowTitle("Browser Settings")
        self.setMinimumWidth(480)
        self.setWindowIcon(icon("settings.png"))
        self.init_ui()
        self.set_title_bar_color("#f5f6f8")

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
        self.download_dir.setText(self.parent_browser.settings.get(
            "download_dir", str(Path.home() / "Downloads")))
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_download_dir)
        download_row = QHBoxLayout()
        download_row.setSpacing(8)
        download_row.addWidget(self.download_dir, 1)
        download_row.addWidget(browse_btn)
        download_container = QWidget()
        download_container.setLayout(download_row)
        form_layout.addRow("Download Directory:", download_container)

        self.ask_save_check = QCheckBox("Ask where to save each download")
        self.ask_save_check.setChecked(self.parent_browser.settings.get("ask_where_to_save", False))
        form_layout.addRow("", self.ask_save_check)

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
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.parent_browser.settings.get("theme", "Light"))
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

    def browse_download_dir(self):
        chosen = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", self.download_dir.text() or str(Path.home()))
        if chosen:
            self.download_dir.setText(chosen)

    def save_settings(self):
        settings = {
            "home_page": self.home_page_input.text(),
            "download_dir": self.download_dir.text(),
            "ask_where_to_save": self.ask_save_check.isChecked(),
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
        self.ask_save_check.setChecked(False)
        self.javascript_check.setChecked(True)
        self.local_storage_check.setChecked(True)
        self.cookies_check.setChecked(True)
        self.cache_check.setChecked(True)
        self.zoom_spin.setValue(100)
        self.theme_combo.setCurrentText("Light")

    def set_title_bar_color(self, hex_color: str):
        # Convert hex string to COLORREF (BGR format)
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        color_ref = r | (g << 8) | (b << 16)

        try:
            # DWMWA_CAPTION_COLOR attribute ID is 35 on Windows 11
            DWMWA_CAPTION_COLOR = 35
            hwnd = int(self.winId())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_CAPTION_COLOR, 
                ctypes.byref(ctypes.c_uint(color_ref)), 
                ctypes.sizeof(ctypes.c_uint)
            )
        except Exception as e:
            print(f"Failed to set native title bar color: {e}")
