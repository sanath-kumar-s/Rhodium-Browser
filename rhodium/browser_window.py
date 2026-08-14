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
    QMessageBox, QMenu, QInputDialog, QToolBar, QTabWidget, QStatusBar,
    QDialog, QListWidget, QTextEdit, QSizePolicy, QFileDialog, QToolButton, QApplication, QProgressBar, QListWidgetItem, 
    QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtCore import Qt, QUrl, QSize, QPoint, pyqtSignal, QTimer, QObject, QUrl
from PyQt6.QtGui import QAction, QDesktopServices, QKeySequence

from rhodium.utils import icon
from rhodium.resources import get_stylesheet, get_home_page_html
from rhodium.settings_dialog import SettingsDialog
from rhodium.find_bar import FindBar
from rhodium.web_views import RhodiumWebEnginePage, SmoothWebEngineView

class DownloadPopup(QFrame):

    def __init__(
        self,
        parent,
        data,
        completed=False
    ):

        super().__init__(
            parent,
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
        )

        self.data = data
        self.completed = completed

        self.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose
        )

        self.setFixedWidth(
            360
        )

        self.setStyleSheet("""
            QFrame {
                background: #181818;
                border: 1px solid #333333;
                border-radius: 12px;
            }

            QLabel {
                color: #eeeeee;
            }

            QLabel#PopupTitle {
                font-size: 14px;
                font-weight: 700;
            }

            QLabel#PopupInfo {
                color: #999999;
                font-size: 12px;
            }

            QProgressBar {
                background: #292929;
                border: none;
                border-radius: 3px;
                height: 6px;
            }

            QProgressBar::chunk {
                background: #4c8dff;
                border-radius: 3px;
            }
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        layout.setSpacing(8)

        title = QLabel(
            "Download complete"
            if completed
            else "Downloading"
        )

        title.setObjectName(
            "PopupTitle"
        )

        layout.addWidget(
            title
        )

        filename = QLabel(
            data.get(
                "name",
                "Unknown file"
            )
        )

        filename.setObjectName(
            "PopupInfo"
        )

        filename.setWordWrap(
            True
        )

        layout.addWidget(
            filename
        )

        if not completed:

            self.progress = QProgressBar()

            self.progress.setRange(
                0,
                100
            )

            self.progress.setValue(
                0
            )

            self.progress.setTextVisible(
                False
            )

            layout.addWidget(
                self.progress
            )

            self.info = QLabel(
                "Starting..."
            )

            self.info.setObjectName(
                "PopupInfo"
            )

            layout.addWidget(
                self.info
            )

        else:

            info = QLabel(
                "Download finished successfully."
            )

            info.setObjectName(
                "PopupInfo"
            )

            layout.addWidget(
                info
            )

        # Position near bottom-right
        self.move_popup()

        if not completed:

            self.timer = QTimer(self)

            self.timer.timeout.connect(
                self.update_popup
            )

            self.timer.start(
                250
            )

        else:

            QTimer.singleShot(
                3500,
                self.close
            )

    def move_popup(self):

        screen = QApplication.primaryScreen()

        if screen is None:
            return

        geometry = screen.availableGeometry()

        x = (
            geometry.right()
            - self.width()
            - 20
        )

        y = (
            geometry.bottom()
            - self.height()
            - 20
        )

        self.move(
            x,
            y
        )

    def update_popup(self):

        download = self.data.get(
            "download"
        )

        if download is None:
            return

        received = download.receivedBytes()
        total = download.totalBytes()

        if total > 0:

            percent = int(
                received * 100 / total
            )

            self.progress.setValue(
                percent
            )

            self.info.setText(
                f"{percent}% — "
                f"{DownloadManager.format_bytes(received)} / "
                f"{DownloadManager.format_bytes(total)}"
            )

        else:

            self.info.setText(
                DownloadManager.format_bytes(
                    received
                )
            )


class DownloadManager(QObject):

    def __init__(self, browser):
        super().__init__(browser)

        self.browser = browser

        self.downloads = {}

        self.next_id = 1

        self.downloads_file = (
            Path.home()
            / ".rhodium"
            / "downloads.json"
        )

        self.downloads_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.history = self.load_history()

        self.download_dialog = None

        self.init_styles()

    # =============================================================
    # STYLING
    # =============================================================

    def init_styles(self):

        self.style = """
        QDialog#DownloadsDialog {
            background: #111111;
        }

        QFrame#DownloadItem {
            background: #191919;
            border: 1px solid #292929;
            border-radius: 10px;
        }

        QLabel#DownloadFileName {
            color: #eeeeee;
            font-size: 14px;
            font-weight: 600;
        }

        QLabel#DownloadStatus {
            color: #888888;
            font-size: 12px;
        }

        QLabel#DownloadInfo {
            color: #888888;
            font-size: 12px;
        }

        QProgressBar {
            background: #292929;
            border: none;
            border-radius: 3px;
        }

        QProgressBar::chunk {
            background: #4c8dff;
            border-radius: 3px;
        }

        QPushButton#DownloadActionButton,
        QPushButton#DownloadCancelButton {
            background: #242424;
            color: #dddddd;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
        }

        QPushButton#DownloadActionButton:hover {
            background: #333333;
        }

        QPushButton#DownloadCancelButton:hover {
            background: #642c2c;
        }

        QLabel#DownloadsTitle {
            color: white;
            font-size: 20px;
            font-weight: 700;
        }

        QLabel#EmptyDownloads {
            color: #777777;
            font-size: 14px;
        }
        """

    # =============================================================
    # FILE SIZE
    # =============================================================

    @staticmethod
    def format_bytes(value):

        if value is None or value < 0:
            return "Unknown"

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]

        size = float(value)

        for unit in units:

            if size < 1024:
                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{size:.1f} PB"

    # =============================================================
    # SPEED
    # =============================================================

    @staticmethod
    def format_speed(value):

        if value <= 0:
            return "0 B/s"

        return (
            DownloadManager.format_bytes(value)
            + "/s"
        )

    # =============================================================
    # ETA
    # =============================================================

    @staticmethod
    def format_eta(seconds):

        if seconds is None or seconds <= 0:
            return "Calculating..."

        seconds = int(seconds)

        minutes, seconds = divmod(
            seconds,
            60
        )

        hours, minutes = divmod(
            minutes,
            60
        )

        if hours:
            return f"{hours}h {minutes}m left"

        if minutes:
            return f"{minutes}m {seconds}s left"

        return f"{seconds}s left"

    # =============================================================
    # HISTORY
    # =============================================================

    def load_history(self):

        try:

            if self.downloads_file.exists():

                return json.loads(
                    self.downloads_file.read_text(
                        encoding="utf-8"
                    )
                )

        except Exception as e:

            print(
                "Could not load download history:",
                e
            )

        return []

    def save_history(self):

        try:

            self.downloads_file.write_text(
                json.dumps(
                    self.history,
                    indent=2
                ),
                encoding="utf-8"
            )

        except Exception as e:

            print(
                "Could not save download history:",
                e
            )

    # =============================================================
    # DOWNLOAD REQUEST
    # =============================================================

    def on_download_requested(self, download):

        suggested_name = (
            download.suggestedFileName()
        )

        if not suggested_name:

            suggested_name = "download"

        download_dir = self.browser.settings.get(
            "download_dir",
            str(
                Path.home()
                / "Downloads"
            )
        )

        Path(download_dir).mkdir(
            parents=True,
            exist_ok=True
        )

        # ---------------------------------------------------------
        # ASK USER WHERE TO SAVE
        # ---------------------------------------------------------

        save_path, selected_filter = QFileDialog.getSaveFileName(
            self.browser,
            "Save file",
            str(
                Path(download_dir)
                / suggested_name
            ),
            "All Files (*)"
        )

        if not save_path:

            download.cancel()
            return

        save_path = os.path.abspath(
            save_path
        )

        directory = os.path.dirname(
            save_path
        )

        filename = os.path.basename(
            save_path
        )

        # ---------------------------------------------------------
        # CREATE DOWNLOAD RECORD
        # ---------------------------------------------------------

        download_id = self.next_id

        self.next_id += 1

        data = {

            "id": download_id,

            "name": filename,

            "path": save_path,

            "url": download.url().toString(),

            "date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "state": "downloading",

            "download": download,

            "widget": None,

            "received": 0,

            "total": 0,

            "last_bytes": 0,

            "last_time": time.monotonic(),

            "speed": 0,

            "paused": False,
        }

        self.downloads[
            download_id
        ] = data

        # ---------------------------------------------------------
        # SET DESTINATION
        # ---------------------------------------------------------

        download.setDownloadDirectory(
            directory
        )

        download.setDownloadFileName(
            filename
        )

        # ---------------------------------------------------------
        # CREATE UI
        # ---------------------------------------------------------

        widget = DownloadItemWidget(
            self,
            download_id,
            data
        )

        data["widget"] = widget

        # ---------------------------------------------------------
        # SIGNALS
        # ---------------------------------------------------------

        download.receivedBytesChanged.connect(
            lambda did=download_id:
                self.update_progress(did)
        )

        download.totalBytesChanged.connect(
            lambda did=download_id:
                self.update_progress(did)
        )

        download.stateChanged.connect(
            lambda state, did=download_id:
                self.download_state_changed(
                    did,
                    state
                )
        )

        # ---------------------------------------------------------
        # START
        # ---------------------------------------------------------

        download.accept()

        self.add_download_to_ui(
            download_id
        )

        self.show_download_popup(
            download_id
        )

    # =============================================================
    # ADD TO DOWNLOAD WINDOW
    # =============================================================

    def add_download_to_ui(self, download_id):

        if self.download_dialog is None:

            self.create_download_dialog()

        data = self.downloads[
            download_id
        ]

        item = QListWidgetItem()

        item.setSizeHint(
            data["widget"].sizeHint()
        )

        self.download_list.insertItem(
            0,
            item
        )

        self.download_list.setItemWidget(
            item,
            data["widget"]
        )

    # =============================================================
    # PROGRESS
    # =============================================================

    def update_progress(self, download_id):

        data = self.downloads.get(
            download_id
        )

        if data is None:
            return

        download = data["download"]

        received = download.receivedBytes()
        total = download.totalBytes()

        now = time.monotonic()

        elapsed = (
            now
            - data["last_time"]
        )

        if elapsed >= 0.25:

            speed = (
                received
                - data["last_bytes"]
            ) / elapsed

            data["speed"] = max(
                0,
                speed
            )

            data["last_bytes"] = received
            data["last_time"] = now

        data["received"] = received
        data["total"] = total

        if total > 0:

            percent = int(
                received * 100 / total
            )

            remaining = max(
                0,
                total - received
            )

            if data["speed"] > 0:

                eta = (
                    remaining
                    / data["speed"]
                )

            else:

                eta = None

        else:

            percent = 0
            eta = None

        widget = data["widget"]

        if widget:

            widget.update_progress(
                percent,
                received,
                total,
                data["speed"],
                eta
            )

        self.browser.status_label.setText(
            f"Downloading {data['name']} — "
            f"{percent}%"
        )

    # =============================================================
    # STATE
    # =============================================================

    def download_state_changed(
        self,
        download_id,
        state
    ):

        from PyQt6.QtWebEngineCore import (
            QWebEngineDownloadRequest
        )

        data = self.downloads.get(
            download_id
        )

        if data is None:
            return

        widget = data["widget"]

        if state == (
            QWebEngineDownloadRequest.DownloadState.DownloadCompleted
        ):

            self.download_completed(
                download_id
            )

        elif state == (
            QWebEngineDownloadRequest.DownloadState.DownloadCancelled
        ):

            data["state"] = "cancelled"

            if widget:
                widget.mark_cancelled()

            self.browser.status_label.setText(
                "Download cancelled"
            )

        elif state == (
            QWebEngineDownloadRequest.DownloadState.DownloadInterrupted
        ):

            data["state"] = "failed"

            if widget:
                widget.mark_failed(
                    "Download interrupted"
                )

            self.browser.status_label.setText(
                "Download interrupted"
            )

    # =============================================================
    # COMPLETED
    # =============================================================

    def download_completed(
        self,
        download_id
    ):

        data = self.downloads.get(
            download_id
        )

        if data is None:
            return

        data["state"] = "completed"

        path = data["path"]

        data["completed"] = True

        # ---------------------------------------------------------
        # SAVE HISTORY
        # ---------------------------------------------------------

        history_entry = {

            "name": data["name"],

            "path": path,

            "url": data["url"],

            "date": data["date"],

            "state": "completed",
        }

        self.history.append(
            history_entry
        )

        self.save_history()

        # ---------------------------------------------------------
        # UI
        # ---------------------------------------------------------

        widget = data["widget"]

        if widget:
            widget.mark_finished()

        self.browser.status_label.setText(
            f"Download complete: {data['name']}"
        )

        self.show_completion_popup(
            data
        )

    # =============================================================
    # REMOVE
    # =============================================================

    def remove_download(
        self,
        download_id
    ):

        data = self.downloads.pop(
            download_id,
            None
        )

        if data is None:
            return

        widget = data["widget"]

        if widget:

            item = self.download_list.itemAt(
                0
            )

            # Find the QListWidgetItem containing widget
            for i in range(
                self.download_list.count()
            ):

                current_item = (
                    self.download_list.item(i)
                )

                if (
                    self.download_list.itemWidget(
                        current_item
                    )
                    is widget
                ):

                    self.download_list.takeItem(i)

                    break

    # =============================================================
    # DOWNLOAD WINDOW
    # =============================================================

    def create_download_dialog(self):

        self.download_dialog = QDialog(
            self.browser
        )

        self.download_dialog.setObjectName(
            "DownloadsDialog"
        )

        self.download_dialog.setWindowTitle(
            "Rhodium Downloads"
        )

        self.download_dialog.setMinimumSize(
            760,
            520
        )

        self.download_dialog.resize(
            850,
            600
        )

        self.download_dialog.setStyleSheet(
            self.style
        )

        layout = QVBoxLayout(
            self.download_dialog
        )

        layout.setContentsMargins(
            20,
            18,
            20,
            20
        )

        layout.setSpacing(14)

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        header = QHBoxLayout()

        title = QLabel(
            "Downloads"
        )

        title.setObjectName(
            "DownloadsTitle"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        self.clear_btn = QPushButton(
            "Clear history"
        )

        self.clear_btn.clicked.connect(
            self.clear_history
        )

        header.addWidget(
            self.clear_btn
        )

        layout.addLayout(
            header
        )

        # ---------------------------------------------------------
        # LIST
        # ---------------------------------------------------------

        self.download_list = QListWidget()

        self.download_list.setSpacing(
            8
        )

        self.download_list.setFrameShape(
            QFrame.Shape.NoFrame
        )

        layout.addWidget(
            self.download_list
        )

        self.populate_history()

    # =============================================================
    # SHOW DOWNLOADS
    # =============================================================

    def show_downloads(self):

        if self.download_dialog is None:

            self.create_download_dialog()

        self.download_dialog.show()

        self.download_dialog.raise_()

        self.download_dialog.activateWindow()

    # =============================================================
    # HISTORY
    # =============================================================

    def populate_history(self):

        if not hasattr(
            self,
            "download_list"
        ):
            return

        self.download_list.clear()

        # Current downloads
        for download_id in reversed(
            list(self.downloads.keys())
        ):

            data = self.downloads[
                download_id
            ]

            item = QListWidgetItem()

            item.setSizeHint(
                data["widget"].sizeHint()
            )

            self.download_list.addItem(
                item
            )

            self.download_list.setItemWidget(
                item,
                data["widget"]
            )

    # =============================================================
    # CLEAR HISTORY
    # =============================================================

    def clear_history(self):

        reply = QMessageBox.question(
            self.download_dialog,
            "Clear download history",
            "Remove all completed download history?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.history.clear()

        self.save_history()

    # =============================================================
    # POPUP
    # =============================================================

    def show_download_popup(
        self,
        download_id
    ):

        data = self.downloads.get(
            download_id
        )

        if not data:
            return

        popup = DownloadPopup(
            self.browser,
            data
        )

        popup.show()

    # =============================================================
    # COMPLETION POPUP
    # =============================================================

    def show_completion_popup(
        self,
        data
    ):

        popup = DownloadPopup(
            self.browser,
            data,
            completed=True
        )

        popup.show()


class DownloadItemWidget(QFrame):
    """
    UI representation of a single browser download.
    """

    def __init__(self, manager, download_id, data):
        super().__init__()

        self.manager = manager
        self.download_id = download_id
        self.data = data

        self.setObjectName("DownloadItem")
        self.setMinimumHeight(105)

        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(7)

        # ---------------------------------------------------------
        # TOP ROW
        # ---------------------------------------------------------

        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        self.name_label = QLabel(
            self.data.get("name", "Unknown file")
        )

        self.name_label.setObjectName("DownloadFileName")
        self.name_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        top_layout.addWidget(
            self.name_label,
            1
        )

        self.status_label = QLabel("Starting...")
        self.status_label.setObjectName("DownloadStatus")

        top_layout.addWidget(
            self.status_label
        )

        main_layout.addLayout(top_layout)

        # ---------------------------------------------------------
        # PROGRESS BAR
        # ---------------------------------------------------------

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)

        main_layout.addWidget(self.progress)

        # ---------------------------------------------------------
        # BOTTOM ROW
        # ---------------------------------------------------------

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.info_label = QLabel("Preparing...")
        self.info_label.setObjectName("DownloadInfo")

        bottom_layout.addWidget(
            self.info_label,
            1
        )

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setObjectName("DownloadActionButton")
        self.pause_btn.clicked.connect(
            self.toggle_pause
        )

        self.open_btn = QPushButton("Open")
        self.open_btn.setObjectName("DownloadActionButton")
        self.open_btn.clicked.connect(
            self.open_file
        )
        self.open_btn.hide()

        self.folder_btn = QPushButton("Show in folder")
        self.folder_btn.setObjectName("DownloadActionButton")
        self.folder_btn.clicked.connect(
            self.open_folder
        )
        self.folder_btn.hide()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("DownloadCancelButton")
        self.cancel_btn.clicked.connect(
            self.cancel_download
        )

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("DownloadActionButton")
        self.remove_btn.clicked.connect(
            self.remove_download
        )
        self.remove_btn.hide()

        bottom_layout.addWidget(self.pause_btn)
        bottom_layout.addWidget(self.open_btn)
        bottom_layout.addWidget(self.folder_btn)
        bottom_layout.addWidget(self.cancel_btn)
        bottom_layout.addWidget(self.remove_btn)

        main_layout.addLayout(bottom_layout)

    # =============================================================
    # UPDATE
    # =============================================================

    def update_progress(
        self,
        percent,
        received,
        total,
        speed,
        eta
    ):

        self.progress.setValue(percent)

        received_text = self.manager.format_bytes(received)

        if total > 0:

            total_text = self.manager.format_bytes(total)

            self.info_label.setText(
                f"{received_text} / {total_text}   •   "
                f"{self.manager.format_speed(speed)}   •   "
                f"{self.manager.format_eta(eta)}"
            )

        else:

            self.info_label.setText(
                f"{received_text}   •   "
                f"{self.manager.format_speed(speed)}"
            )

        self.status_label.setText(
            f"{percent}%"
        )

    # =============================================================
    # PAUSE / RESUME
    # =============================================================

    def toggle_pause(self):

        download = self.data.get("download")

        if download is None:
            return

        if self.data.get("paused", False):

            download.resume()

            self.data["paused"] = False
            self.pause_btn.setText("Pause")
            self.status_label.setText("Downloading...")

        else:

            download.pause()

            self.data["paused"] = True
            self.pause_btn.setText("Resume")
            self.status_label.setText("Paused")

    # =============================================================
    # CANCEL
    # =============================================================

    def cancel_download(self):

        download = self.data.get("download")

        if download is not None:
            download.cancel()

    # =============================================================
    # OPEN FILE
    # =============================================================

    def open_file(self):

        path = self.data.get("path")

        if not path:
            return

        if not os.path.exists(path):
            QMessageBox.warning(
                self,
                "File not found",
                "The downloaded file no longer exists."
            )
            return

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(path)
        )

    # =============================================================
    # OPEN FOLDER
    # =============================================================

    def open_folder(self):

        path = self.data.get("path")

        if not path:
            return

        folder = os.path.dirname(path)

        if os.path.exists(folder):

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(folder)
            )

    # =============================================================
    # REMOVE
    # =============================================================

    def remove_download(self):

        self.manager.remove_download(
            self.download_id
        )

    # =============================================================
    # FINISHED
    # =============================================================

    def mark_finished(self):

        self.status_label.setText("Completed")
        self.progress.setValue(100)

        self.pause_btn.hide()
        self.cancel_btn.hide()

        self.open_btn.show()
        self.folder_btn.show()
        self.remove_btn.show()

    # =============================================================
    # FAILED
    # =============================================================

    def mark_failed(self, reason="Download failed"):

        self.status_label.setText("Failed")

        self.info_label.setText(reason)

        self.pause_btn.hide()
        self.cancel_btn.hide()

        self.remove_btn.show()

    # =============================================================
    # CANCELLED
    # =============================================================

    def mark_cancelled(self):

        self.status_label.setText("Cancelled")

        self.pause_btn.hide()
        self.cancel_btn.hide()

        self.remove_btn.show()

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
        # self.downloads = self.load_downloads()

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
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("BrowserTabs")

        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(True)

        self.tab_widget.setMovable(True)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)

        self.tab_widget.tabBar().setMinimumHeight(38)
        self.tab_widget.tabBar().setExpanding(False)

        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)

        # NEW TAB BUTTON
        self.new_tab_button = QToolButton()
        self.new_tab_button.setObjectName("NewTabButton")
        self.new_tab_button.setIcon(icon("plus.png"))
        self.new_tab_button.setIconSize(QSize(16, 16))
        self.new_tab_button.setFixedSize(32, 32)
        self.new_tab_button.setAutoRaise(True)
        self.new_tab_button.setToolTip("New Tab  (Ctrl+T)")
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())

        self.download_manager = DownloadManager(self)

        self.tab_widget.setCornerWidget(
            self.new_tab_button,
            Qt.Corner.TopRightCorner
        )

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
        self._add_shortcut("Ctrl+J",       self.download_manager.show_downloads)
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
        self.btn_download = QPushButton()
        self.btn_download.setObjectName("NavBtn")
        self.btn_download.setIcon(icon("download.png"))
        self.btn_download.setIconSize(QSize(17, 17))
        self.btn_download.setFixedSize(34, 34)
        self.btn_download.setToolTip("Downloads  (Ctrl+J)")
        self.download_manager = DownloadManager(self)
        self.btn_download.clicked.connect(self.download_manager.show_downloads)
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
            self.btn_maximize.setIconSize(QSize(12, 12))
            self.setGeometry(80, 80, 1280, 820)
        else:
            self.showMaximized()
            self.btn_maximize.setIconSize(QSize(14, 14))

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

        self.download_manager = DownloadManager(self)
        m.addSection("Tools")
        m.addAction(icon("download.png"),  "Downloads",         self.download_manager.show_downloads).setShortcut(QKeySequence("Ctrl+J"))
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
        page = RhodiumWebEnginePage(self, view)
        view.setPage(page)

        view.setZoomFactor(self.settings.get("default_zoom", 100) / 100.0)

        view.loadStarted.connect(lambda: self.on_load_started(view))
        view.loadProgress.connect(lambda p: self.on_load_progress(p, view))
        view.loadFinished.connect(lambda ok: self.on_load_finished(ok, view))
        view.titleChanged.connect(lambda t: self.on_title_changed(t, view))
        view.urlChanged.connect(lambda u: self.on_url_changed(u, view))

        page.profile().downloadRequested.connect(self.download_manager.on_download_requested)

        idx = self.tab_widget.addTab(view, "New Tab")
        self.tab_widget.setCurrentIndex(idx)
        self.tab_widget.setTabToolTip(idx, "New Tab")

        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(), QUrl("about:blank"))
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
            view.setHtml(get_home_page_html(), QUrl("about:blank"))
        else:
            self._load_in_view(url, view)

    def load_url(self, url: str):
        view = self.get_current_view()
        if not view:
            return
        if url in ("about:home", "rhodium://home"):
            view.setHtml(get_home_page_html(), QUrl("about:blank"))
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
        # Imports here to avoid circular imports during direct instantiation
        from browser_window import AdvancedBrowser
        from window_filter import ResizeMoveFilter
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
        self.download_manager = DownloadManager(self)

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

        if self.get_current_view() == view:
            self.status_label.setText("Done" if ok else "Failed to load page")
            self.url_bar.setText("rhodium://home" if url in ("about:blank", "") else url)
            self._update_bookmark_icon(url)

        if ok and url not in ("about:blank", ""):
            self.add_to_history(url, title)

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
