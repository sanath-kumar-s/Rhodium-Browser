import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QListWidget, QListWidgetItem, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from rhodium.utils import icon

class DownloadPopup(QFrame):
    def __init__(self, parent, data, completed=False):
        super().__init__(
            parent,
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.data = data
        self.completed = completed
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedWidth(360)
        
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
            QPushButton#CloseBtn {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#CloseBtn:hover {
                color: white;
            }
            QPushButton#CancelBtn {
                background: #242424;
                color: #dddddd;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton#CancelBtn:hover {
                background: #642c2c;
            }
            QPushButton#ActionBtn {
                background: #315f9d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton#ActionBtn:hover {
                background: #3b6fae;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header Row
        header = QHBoxLayout()
        title = QLabel("Download Complete" if completed else "Downloading")
        title.setObjectName("PopupTitle")
        header.addWidget(title, 1)

        close_btn = QPushButton("×")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)
        layout.addLayout(header)

        filename = QLabel(data.get("name", "Unknown file"))
        filename.setObjectName("PopupInfo")
        filename.setWordWrap(True)
        layout.addWidget(filename)

        if not completed:
            self.progress = QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.setTextVisible(False)
            layout.addWidget(self.progress)

            self.info = QLabel("Starting...")
            self.info.setObjectName("PopupInfo")
            
            bottom_row = QHBoxLayout()
            bottom_row.addWidget(self.info, 1)
            
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.setObjectName("CancelBtn")
            self.cancel_btn.clicked.connect(self.cancel_download)
            bottom_row.addWidget(self.cancel_btn)
            layout.addLayout(bottom_row)
        else:
            self.info = QLabel("Finished successfully.")
            self.info.setObjectName("PopupInfo")
            
            bottom_row = QHBoxLayout()
            bottom_row.addWidget(self.info, 1)
            
            self.open_btn = QPushButton("Open")
            self.open_btn.setObjectName("ActionBtn")
            self.open_btn.clicked.connect(self.open_file)
            bottom_row.addWidget(self.open_btn)
            layout.addLayout(bottom_row)

        self.move_popup()

        if not completed:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_popup)
            self.timer.start(250)
        else:
            QTimer.singleShot(4000, self.close)

    def move_popup(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geom = screen.availableGeometry()
        x = geom.right() - self.width() - 20
        y = geom.bottom() - self.height() - 20
        self.move(x, y)

    def update_popup(self):
        download = self.data.get("download")
        if download is None or self.data.get("state") in ("completed", "failed", "cancelled"):
            self.timer.stop()
            self.close()
            return

        received = download.receivedBytes()
        total = download.totalBytes()
        speed = self.data.get("speed", 0)
        percent = int(received * 100 / total) if total > 0 else 0

        self.progress.setValue(percent)
        
        speed_text = DownloadManager.format_speed(speed)
        size_text = f"{DownloadManager.format_bytes(received)} / {DownloadManager.format_bytes(total)}"
        self.info.setText(f"{percent}% • {speed_text} • {size_text}")

    def cancel_download(self):
        download = self.data.get("download")
        if download:
            download.cancel()
        self.close()

    def open_file(self):
        path = self.data.get("path")
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        self.close()

class DownloadItemWidget(QFrame):
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

        top_layout = QHBoxLayout()
        self.name_label = QLabel(self.data.get("name", "Unknown file"))
        self.name_label.setObjectName("DownloadFileName")
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        top_layout.addWidget(self.name_label, 1)

        self.status_label = QLabel("Preparing...")
        self.status_label.setObjectName("DownloadStatus")
        top_layout.addWidget(self.status_label)
        main_layout.addLayout(top_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        main_layout.addWidget(self.progress)

        bottom_layout = QHBoxLayout()
        self.info_label = QLabel("Starting...")
        self.info_label.setObjectName("DownloadInfo")
        bottom_layout.addWidget(self.info_label, 1)

        self.open_btn = QPushButton("Open")
        self.open_btn.setObjectName("DownloadActionButton")
        self.open_btn.clicked.connect(self.open_file)
        self.open_btn.hide()

        self.folder_btn = QPushButton("Show in folder")
        self.folder_btn.setObjectName("DownloadActionButton")
        self.folder_btn.clicked.connect(self.open_folder)
        self.folder_btn.hide()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("DownloadCancelButton")
        self.cancel_btn.clicked.connect(self.cancel_download)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("DownloadActionButton")
        self.remove_btn.clicked.connect(self.remove_download)
        self.remove_btn.hide()

        bottom_layout.addWidget(self.open_btn)
        bottom_layout.addWidget(self.folder_btn)
        bottom_layout.addWidget(self.cancel_btn)
        bottom_layout.addWidget(self.remove_btn)
        main_layout.addLayout(bottom_layout)

    def update_progress(self, percent, received, total, speed, eta):
        self.progress.setValue(percent)
        received_text = DownloadManager.format_bytes(received)
        if total > 0:
            total_text = DownloadManager.format_bytes(total)
            self.info_label.setText(
                f"{received_text} / {total_text}   •   "
                f"{DownloadManager.format_speed(speed)}   •   "
                f"{DownloadManager.format_eta(eta)}"
            )
        else:
            self.info_label.setText(
                f"{received_text}   •   "
                f"{DownloadManager.format_speed(speed)}"
            )
        self.status_label.setText(f"{percent}%")

    def cancel_download(self):
        download = self.data.get("download")
        if download:
            download.cancel()

    def open_file(self):
        path = self.data.get("path")
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "File not found", "The file no longer exists.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def open_folder(self):
        path = self.data.get("path")
        if not path:
            return
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            if sys.platform == "win32":
                os.system(f'explorer /select,"{os.path.normpath(path)}"')
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def remove_download(self):
        self.manager.remove_download(self.download_id)

    def mark_finished(self):
        self.status_label.setText("Completed")
        self.progress.setValue(100)
        self.cancel_btn.hide()
        self.open_btn.show()
        self.folder_btn.show()
        self.remove_btn.show()

    def mark_failed(self, reason="Download failed"):
        self.status_label.setText("Failed")
        self.info_label.setText(reason)
        self.cancel_btn.hide()
        self.remove_btn.show()

    def mark_cancelled(self):
        self.status_label.setText("Cancelled")
        self.cancel_btn.hide()
        self.remove_btn.show()

class DownloadManager(QObject):
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser
        self.downloads = {}
        self.next_id = 1
        
        self.downloads_file = Path.home() / ".rhodium" / "downloads.json"
        self.downloads_file.parent.mkdir(parents=True, exist_ok=True)
        self.history = self.load_history()
        self.download_dialog = None

    def load_history(self):
        try:
            if self.downloads_file.exists():
                return json.loads(self.downloads_file.read_text(encoding="utf-8"))
        except Exception as e:
            print("Could not load download history:", e)
        return []

    def save_history(self):
        try:
            clean_history = []
            for item in self.history:
                clean_item = item.copy()
                if "download" in clean_item:
                    del clean_item["download"]
                if "widget" in clean_item:
                    del clean_item["widget"]
                clean_history.append(clean_item)
            self.downloads_file.write_text(json.dumps(clean_history, indent=2), encoding="utf-8")
        except Exception as e:
            print("Could not save download history:", e)

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        # Prevent double handling
        if download.id() in [d.get("download").id() for d in self.downloads.values() if d.get("download")]:
            return

        suggested_name = download.suggestedFileName() or "download"
        download_dir = self.browser.settings.get("download_dir", str(Path.home() / "Downloads"))
        
        base_name, ext = os.path.splitext(suggested_name)
        target_path = Path(download_dir) / suggested_name
        counter = 1
        while target_path.exists():
            target_path = Path(download_dir) / f"{base_name} ({counter}){ext}"
            counter += 1

        # Must configure BEFORE accept()
        download.setDownloadDirectory(str(target_path.parent))
        download.setDownloadFileName(target_path.name)

        download_id = self.next_id
        self.next_id += 1

        data = {
            "id": download_id,
            "name": target_path.name,
            "path": str(target_path),
            "url": download.url().toString(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "state": "downloading",
            "download": download,
            "widget": None,
            "received": 0,
            "total": 0,
            "last_bytes": 0,
            "last_time": time.monotonic(),
            "speed": 0,
        }

        self.downloads[download_id] = data

        download.receivedBytesChanged.connect(lambda: self.update_progress(download_id))
        download.totalBytesChanged.connect(lambda: self.update_progress(download_id))
        download.stateChanged.connect(lambda state: self.download_state_changed(download_id, state))

        download.accept()

        widget = DownloadItemWidget(self, download_id, data)
        data["widget"] = widget

        self.add_download_to_ui(download_id)
        
        popup = DownloadPopup(self.browser, data)
        popup.show()

    def update_progress(self, download_id):
        data = self.downloads.get(download_id)
        if not data:
            return
        download = data["download"]
        received = download.receivedBytes()
        total = download.totalBytes()
        now = time.monotonic()
        elapsed = now - data["last_time"]

        if elapsed >= 0.25:
            speed = (received - data["last_bytes"]) / elapsed
            data["speed"] = max(0.0, speed)
            data["last_bytes"] = received
            data["last_time"] = now

        percent = int(received * 100 / total) if total > 0 else 0
        eta = (total - received) / data["speed"] if total > 0 and data["speed"] > 0 else None

        if data["widget"]:
            data["widget"].update_progress(percent, received, total, data["speed"], eta)

        self.browser.status_label.setText(f"Downloading {data['name']} — {percent}%")

    def download_state_changed(self, download_id, state):
        data = self.downloads.get(download_id)
        if not data:
            return
        widget = data["widget"]

        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            data["state"] = "completed"
            self.history.append({
                "name": data["name"],
                "path": data["path"],
                "url": data["url"],
                "date": data["date"],
                "state": "completed"
            })
            self.save_history()
            if widget:
                widget.mark_finished()
            
            popup = DownloadPopup(self.browser, data, completed=True)
            popup.show()
            self.browser.status_label.setText(f"Download complete: {data['name']}")

        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            data["state"] = "cancelled"
            if widget:
                widget.mark_cancelled()
            self.browser.status_label.setText("Download cancelled")

        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            data["state"] = "failed"
            if widget:
                widget.mark_failed("Interrupted")
            self.browser.status_label.setText("Download failed")

    def add_download_to_ui(self, download_id):
        if self.download_dialog is None:
            self.create_download_dialog()
        data = self.downloads[download_id]
        item = QListWidgetItem()
        item.setSizeHint(data["widget"].sizeHint())
        self.download_list.insertItem(0, item)
        self.download_list.setItemWidget(item, data["widget"])

    def create_download_dialog(self):
        self.download_dialog = QDialog(self.browser)
        self.download_dialog.setObjectName("DownloadsDialog")
        self.download_dialog.setWindowTitle("Downloads")
        self.download_dialog.setMinimumSize(760, 520)
        self.download_dialog.resize(850, 600)
        self.download_dialog.setStyleSheet(self.browser.styleSheet())

        layout = QVBoxLayout(self.download_dialog)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Downloads")
        title.setObjectName("DownloadsTitle")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header.addWidget(title)
        header.addStretch()

        clear_btn = QPushButton("Clear history")
        clear_btn.clicked.connect(self.clear_history)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.download_list = QListWidget()
        self.download_list.setSpacing(8)
        self.download_list.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.download_list)

        self.populate_history()

    def populate_history(self):
        if not self.download_dialog:
            return
        self.download_list.clear()

        # Active downloads first
        for download_id in reversed(list(self.downloads.keys())):
            data = self.downloads[download_id]
            item = QListWidgetItem()
            item.setSizeHint(data["widget"].sizeHint())
            self.download_list.addItem(item)
            self.download_list.setItemWidget(item, data["widget"])

        # Then historic completed/failed downloads
        for h in reversed(self.history):
            if any(d["path"] == h["path"] for d in self.downloads.values()):
                continue
            
            # Create a mock/non-active widget
            widget = QFrame()
            widget.setObjectName("DownloadItem")
            widget.setMinimumHeight(80)
            
            w_layout = QVBoxLayout(widget)
            w_layout.setContentsMargins(14, 12, 14, 12)
            
            top = QHBoxLayout()
            name_lbl = QLabel(h["name"])
            name_lbl.setObjectName("DownloadFileName")
            name_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #eeeeee;")
            status_lbl = QLabel(h["state"].capitalize())
            status_lbl.setObjectName("DownloadStatus")
            status_lbl.setStyleSheet("color: #888888; font-size: 12px;")
            top.addWidget(name_lbl, 1)
            top.addWidget(status_lbl)
            w_layout.addLayout(top)
            
            bottom = QHBoxLayout()
            info_lbl = QLabel(f"{h['date']}  •  {h['url']}")
            info_lbl.setObjectName("DownloadInfo")
            info_lbl.setStyleSheet("color: #666666; font-size: 11px;")
            bottom.addWidget(info_lbl, 1)
            
            open_btn = QPushButton("Open")
            open_btn.setObjectName("DownloadActionButton")
            open_btn.clicked.connect(lambda checked, p=h["path"]: QDesktopServices.openUrl(QUrl.fromLocalFile(p)))
            
            folder_btn = QPushButton("Show in folder")
            folder_btn.setObjectName("DownloadActionButton")
            
            def show_in_folder_fn(p=h["path"]):
                if sys.platform == "win32":
                    os.system(f'explorer /select,"{os.path.normpath(p)}"')
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(p)))
            folder_btn.clicked.connect(show_in_folder_fn)

            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("DownloadActionButton")
            
            def remove_history_fn(entry=h):
                if entry in self.history:
                    self.history.remove(entry)
                    self.save_history()
                self.populate_history()
            remove_btn.clicked.connect(remove_history_fn)

            bottom.addWidget(open_btn)
            bottom.addWidget(folder_btn)
            bottom.addWidget(remove_btn)
            w_layout.addLayout(bottom)

            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.download_list.addItem(item)
            self.download_list.setItemWidget(item, widget)

    def show_downloads(self):
        if self.download_dialog is None:
            self.create_download_dialog()
        self.populate_history()
        self.download_dialog.show()
        self.download_dialog.raise_()
        self.download_dialog.activateWindow()

    def remove_download(self, download_id):
        data = self.downloads.pop(download_id, None)
        if data:
            self.populate_history()

    def clear_history(self):
        reply = QMessageBox.question(
            self.download_dialog,
            "Clear download history",
            "Remove all completed download history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.save_history()
            self.populate_history()

    @staticmethod
    def format_bytes(value):
        if value is None or value < 0:
            return "Unknown"
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(value)
        for unit in units:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    @staticmethod
    def format_speed(value):
        if value <= 0:
            return "0 B/s"
        return f"{DownloadManager.format_bytes(value)}/s"

    @staticmethod
    def format_eta(seconds):
        if seconds is None or seconds <= 0:
            return "Calculating..."
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minutes}m left"
        if minutes:
            return f"{minutes}m {seconds}s left"
        return f"{seconds}s left"
