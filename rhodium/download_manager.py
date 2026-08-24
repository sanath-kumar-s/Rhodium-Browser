import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import QFileDialog, QApplication


class DownloadState:
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


TERMINAL_STATES = {DownloadState.COMPLETED, DownloadState.FAILED,
                   DownloadState.CANCELLED, DownloadState.INTERRUPTED}

EXECUTABLE_EXTS = {".exe", ".msi", ".msix", ".msp", ".bat", ".cmd",
                   ".ps1", ".scr", ".com", ".jar", ".vbs"}

MULTI_SUFFIXES = (".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst")

INTERRUPT_MESSAGES = {
    "FILE_NO_SPACE": "There isn't enough storage space to complete this download.",
    "FILE_FAILED": "The file could not be written to disk.",
    "FILE_ACCESS_DENIED": "Access to the download location was denied.",
    "FILE_HASH_MISMATCH": "The download appears to be corrupted.",
    "FILE_TOO_LARGE": "The file is too large for the file system.",
    "FILE_VIRUS_INFECTED": "A virus was detected in the file.",
    "FILE_BLOCKED": "The file was blocked on this computer.",
    "FILE_SECURITY_CHECK_FAILED": "The security scan of the file failed.",
    "NETWORK_FAILED": "The connection was interrupted.",
    "NETWORK_TIMEOUT": "The connection timed out.",
    "NETWORK_DISCONNECTED": "The network connection was lost.",
    "NETWORK_SERVER_DOWN": "The server is unavailable.",
    "NETWORK_INVALID_REQUEST": "The download request was invalid.",
    "SERVER_BAD_CONTENT": "The server reported that the file does not exist.",
    "SERVER_FAILED": "The server reported an error.",
    "SERVER_FORBIDDEN": "The server refused the download.",
    "SERVER_UNAUTHORIZED": "The server requires authorization.",
    "SERVER_CONTENT_LENGTH_MISMATCH": "The connection ended unexpectedly.",
    "SERVER_CROSS_ORIGIN_REDIRECT": "The download was redirected to an untrusted source.",
    "USER_CANCELED": "The download was cancelled.",
    "USER_SHUTDOWN": "The download was interrupted by shutdown.",
    "CRASH": "The browser crashed during the download.",
}

NETWORK_ERROR_MESSAGES = {
    "ConnectionRefusedError": "The connection was refused.",
    "RemoteHostClosedError": "The connection was interrupted.",
    "HostNotFoundError": "The server could not be found.",
    "TimeoutError": "The connection timed out.",
    "OperationCanceledError": "The download was cancelled.",
    "AuthenticationRequiredError": "The server requires authorization.",
    "ContentAccessDenied": "Access to the file was denied.",
    "UnknownContentError": "The server sent an unexpected response.",
    "ProtocolFailure": "A network protocol error occurred.",
}


def format_bytes(value) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "Unknown"
    if value < 0:
        return "Unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = value
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_speed(bytes_per_second: float) -> str:
    if bytes_per_second <= 0:
        return ""
    return format_bytes(bytes_per_second) + "/s"


def format_eta(seconds) -> str:
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "Calculating…"
    if seconds < 0 or seconds != seconds:
        return "Calculating…"
    if seconds < 5:
        return "a few seconds"
    if seconds < 60:
        return f"{int(seconds)} sec"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    return f"{hours} hr {minutes % 60} min"


def unique_path(directory: Path, filename: str) -> Path:
    filename = filename.strip() or "download"
    filename = filename.replace("/", "_").replace("\\", "_")
    lower = filename.lower()
    if lower.endswith(MULTI_SUFFIXES):
        dot = filename.lower().rfind(".tar.")
        base, ext = filename[:dot], filename[dot:]
    else:
        base, ext = Path(filename).stem, Path(filename).suffix
    candidate = directory / filename
    counter = 1
    while candidate.exists():
        candidate = directory / f"{base} ({counter}){ext}"
        counter += 1
    return candidate


class DownloadItem(QObject):
    updated = pyqtSignal()

    def __init__(self, manager: "DownloadManager", url: str, filename: str,
                 save_path, item_id: int, mime_type: str = "", total_size: int = -1):
        super().__init__(manager)
        self.manager = manager
        self.id = item_id
        self.url = url
        self.filename = filename
        self.save_path = str(save_path)
        self.mime_type = mime_type or ""
        self.total_size = total_size
        self.received_size = 0
        self.state = DownloadState.QUEUED
        self.error_message = ""
        self.created_at = datetime.now().isoformat(timespec="seconds")
        self.completed_at = ""
        self.executable = Path(filename).suffix.lower() in EXECUTABLE_EXTS
        self.engine = "webengine"
        self.request = None
        self.reply = None
        self._file = None
        self._speed = 0.0
        self._last_bytes = 0
        self._last_time = time.monotonic()
        self._flushed = 0
        self._resume_base = 0

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def eta(self) -> float:
        if self.total_size > 0 and self._speed > 1.0:
            remaining = (self.total_size - self.received_size) / self._speed
            return max(0.0, remaining)
        return -1.0

    @property
    def percentage(self) -> int:
        if self.state == DownloadState.COMPLETED:
            return 100
        if self.total_size <= 0:
            return -1
        return min(100, int(self.received_size * 100 / self.total_size))

    @property
    def is_active(self) -> bool:
        return self.state in (DownloadState.QUEUED, DownloadState.DOWNLOADING, DownloadState.PAUSED)

    def sample_speed(self):
        now = time.monotonic()
        elapsed = now - self._last_time
        if elapsed < 0.05:
            return
        delta = self.received_size - self._last_bytes
        instant = max(0.0, delta / elapsed)
        self._speed = self._speed * 0.65 + instant * 0.35 if self._speed else instant
        self._last_bytes = self.received_size
        self._last_time = now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "url": self.url,
            "path": self.save_path,
            "mime_type": self.mime_type,
            "total_size": self.total_size,
            "downloaded_size": self.received_size,
            "status": self.state,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error_message,
            "executable": self.executable,
        }

    @classmethod
    def from_dict(cls, manager, data: dict) -> "DownloadItem":
        item = cls(
            manager,
            data.get("url", ""),
            data.get("filename", "download"),
            data.get("path", ""),
            int(data.get("id", 0)),
            data.get("mime_type", ""),
            data.get("total_size", -1),
        )
        item.received_size = data.get("downloaded_size", 0)
        item.state = data.get("status", DownloadState.INTERRUPTED)
        item.created_at = data.get("created_at", "")
        item.completed_at = data.get("completed_at", "")
        item.error_message = data.get("error", "")
        item.executable = bool(data.get("executable")) or \
            Path(item.filename).suffix.lower() in EXECUTABLE_EXTS
        if item.state in (DownloadState.QUEUED, DownloadState.DOWNLOADING, DownloadState.PAUSED):
            item.state = DownloadState.INTERRUPTED
            item.error_message = INTERRUPT_MESSAGES["USER_SHUTDOWN"]
        return item


class DownloadManager(QObject):
    download_added = pyqtSignal(object)
    download_updated = pyqtSignal(object)
    download_removed = pyqtSignal(object)
    history_changed = pyqtSignal()

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser
        self.downloads = {}
        self.next_id = 1
        self.recently_completed_id = None
        self.downloads_file = Path.home() / ".rhodium" / "downloads.json"
        self.downloads_file.parent.mkdir(parents=True, exist_ok=True)
        self._nam = QNetworkAccessManager(self)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(400)
        self._save_timer.timeout.connect(self._save_now)
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(300)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start()
        self._load()

    def _default_dir(self) -> Path:
        return Path(self.browser.settings.get(
            "download_dir", str(Path.home() / "Downloads")))

    def get(self, download_id):
        return self.downloads.get(download_id)

    def active_count(self) -> int:
        return sum(1 for item in self.downloads.values() if item.is_active)

    def overall_progress(self):
        active = [i for i in self.downloads.values()
                  if i.state == DownloadState.DOWNLOADING and i.total_size > 0]
        if not active:
            return None
        received = sum(i.received_size for i in active)
        total = sum(i.total_size for i in active)
        if total <= 0:
            return None
        return received * 100.0 / total

    def on_download_requested(self, request: QWebEngineDownloadRequest):
        if request.state() != QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            return

        if self.browser.settings.get("ask_where_to_save"):
            start_dir = self._default_dir() / (request.suggestedFileName() or "download")
            chosen, _ = QFileDialog.getSaveFileName(
                self.browser, "Save File", str(start_dir))
            if not chosen:
                request.cancel()
                return
            target = Path(chosen)
            target.parent.mkdir(parents=True, exist_ok=True)
            self.browser.settings["download_dir"] = str(target.parent)
            self.browser.save_settings()
            target = unique_path(target.parent, target.name)
        else:
            directory = self._default_dir()
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            target = unique_path(directory, request.suggestedFileName() or "download")

        request.setDownloadDirectory(str(target.parent))
        request.setDownloadFileName(target.name)
        request.accept()

        item = DownloadItem(
            self,
            request.url().toString(),
            request.downloadFileName(),
            Path(request.downloadDirectory()) / request.downloadFileName(),
            self.next_id,
            request.mimeType(),
            request.totalBytes(),
        )
        self.next_id += 1
        item.request = request
        item.engine = "webengine"
        self.downloads[item.id] = item

        request.receivedBytesChanged.connect(lambda it=item: self._sync_progress(it))
        request.totalBytesChanged.connect(lambda it=item: self._sync_total(it))
        request.stateChanged.connect(lambda st, it=item: self._on_webengine_state(it, st))

        self.download_added.emit(item)
        self.download_updated.emit(item)
        self._schedule_save()

    def _sync_progress(self, item: DownloadItem):
        if item.request is None:
            return
        item.received_size = item.request.receivedBytes()
        item.updated.emit()
        self.download_updated.emit(item)

    def _sync_total(self, item: DownloadItem):
        if item.request is None:
            return
        total = item.request.totalBytes()
        if total >= 0:
            item.total_size = total
        item.updated.emit()
        self.download_updated.emit(item)

    def _on_webengine_state(self, item: DownloadItem, state):
        item.sample_speed()
        if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
            item.state = DownloadState.PAUSED if item.request.isPaused() else DownloadState.DOWNLOADING
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self._finish_item(item, DownloadState.COMPLETED)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self._finish_item(item, DownloadState.CANCELLED, cleanup=True)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            reason = item.request.interruptReason()
            reason_name = getattr(reason, "name", "") or ""
            if reason_name == "USER_CANCELED":
                self._finish_item(item, DownloadState.CANCELLED, cleanup=True)
            else:
                item.error_message = INTERRUPT_MESSAGES.get(
                    reason_name, item.request.interruptReasonString())
                self._finish_item(item, DownloadState.INTERRUPTED, cleanup=True)
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_save()

    def _finish_item(self, item: DownloadItem, state: str, cleanup: bool = False):
        item.state = state
        if state == DownloadState.COMPLETED:
            if item.total_size > 0:
                item.received_size = item.total_size
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            item.error_message = ""
            self.recently_completed_id = item.id
        else:
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            if cleanup:
                self._delete_partial(item)
        item.request = None
        item.reply = None
        if state != DownloadState.COMPLETED and item.received_size <= 0:
            item.received_size = 0

    def _delete_partial(self, item: DownloadItem):
        try:
            path = Path(item.save_path)
            if path.exists() and item.state != DownloadState.COMPLETED:
                path.unlink()
        except OSError:
            pass

    def _tick(self):
        for item in list(self.downloads.values()):
            if item.state == DownloadState.DOWNLOADING:
                item.sample_speed()
                item.updated.emit()
                self.download_updated.emit(item)

    def pause(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.is_active:
            return
        if item.engine == "webengine" and item.request is not None:
            item.request.pause()
            item.state = DownloadState.PAUSED
        elif item.engine == "qtnetwork" and item.reply is not None:
            try:
                item.reply.abort()
            except RuntimeError:
                pass
            self._close_file(item)
            item.state = DownloadState.PAUSED
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_save()

    def resume(self, download_id):
        item = self.downloads.get(download_id)
        if item is None:
            return
        if item.state != DownloadState.PAUSED:
            return
        if item.engine == "webengine":
            if item.request is not None:
                item.request.resume()
                item.state = DownloadState.DOWNLOADING
        else:
            self._start_network_download(item, resume_from=item.received_size)
        item.updated.emit()
        self.download_updated.emit(item)

    def cancel(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.is_active:
            return
        if item.engine == "webengine" and item.request is not None:
            item.state = DownloadState.CANCELLED
            item.request.cancel()
        elif item.engine == "qtnetwork":
            item.state = DownloadState.CANCELLED
            if item.reply is not None:
                try:
                    item.reply.abort()
                except RuntimeError:
                    pass
            self._close_file(item)
            self._delete_partial(item)
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            item.reply = None
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_save()

    def retry(self, download_id):
        item = self.downloads.get(download_id)
        retryable = (DownloadState.QUEUED, *TERMINAL_STATES)
        if item is None or item.state not in retryable or \
                not item.url.startswith(("http://", "https://")):
            return
        path = Path(item.save_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()
        except OSError as e:
            item.error_message = f"Cannot prepare download location: {e}"
            item.updated.emit()
            return
        item.state = DownloadState.QUEUED
        item.error_message = ""
        item.completed_at = ""
        item.received_size = 0
        item._speed = 0.0
        item._last_bytes = 0
        item._last_time = time.monotonic()
        item.updated.emit()
        self.download_updated.emit(item)
        self._start_network_download(item, resume_from=0)

    def _start_network_download(self, item: DownloadItem, resume_from: int = 0):
        request = QNetworkRequest(QUrl(item.url))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy)
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader,
                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Rhodium")
        if resume_from > 0:
            request.setRawHeader(b"Range", f"bytes={resume_from}-".encode())

        reply = self._nam.get(request)
        item.reply = reply
        item.engine = "qtnetwork"
        item.state = DownloadState.DOWNLOADING
        item._flushed = 0
        item._resume_base = resume_from

        try:
            mode = "ab" if resume_from > 0 else "wb"
            item._file = open(item.save_path, mode)
        except OSError as e:
            item.state = DownloadState.FAILED
            item.error_message = f"Cannot write file: {e}"
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            reply.deleteLater()
            item.reply = None
            item.updated.emit()
            self.download_updated.emit(item)
            self._schedule_save()
            return

        reply.readyRead.connect(lambda it=item: self._drain_reply(it))

        def on_progress(received, total, it=item):
            it.total_size = (it._resume_base + total) if total >= 0 else it.total_size
            it.received_size = it._resume_base + received
            it.updated.emit()

        reply.downloadProgress.connect(on_progress)

        def on_finished(it=item):
            self._on_network_finished(it)

        reply.finished.connect(on_finished)

    def _drain_reply(self, item: DownloadItem):
        reply = item.reply
        if reply is None or item._file is None:
            return
        data = bytes(reply.readAll())
        if not data:
            return
        try:
            item._file.write(data)
            item._flushed += len(data)
            item.received_size = item._resume_base + item._flushed
        except OSError as e:
            item.error_message = f"Cannot write file: {e}"
            self._on_network_finished(item, forced_error=True)

    def _on_network_finished(self, item: DownloadItem, forced_error: bool = False):
        reply = item.reply
        if reply is None:
            return
        error = reply.error()
        error_name = getattr(error, "name", "") or ""
        self._close_file(item)
        reply.deleteLater()
        item.reply = None

        if item.state == DownloadState.PAUSED or item.state == DownloadState.CANCELLED:
            self._schedule_save()
            return

        if forced_error:
            item.state = DownloadState.FAILED
        elif error == QNetworkReply.NetworkError.NoError:
            item.state = DownloadState.COMPLETED
            if item.total_size > 0:
                item.received_size = item.total_size
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            self.recently_completed_id = item.id
        elif error_name == "OperationCanceledError":
            item.state = DownloadState.CANCELLED
        else:
            item.state = DownloadState.FAILED
            item.error_message = NETWORK_ERROR_MESSAGES.get(error_name, reply.errorString())

        item.updated.emit()
        self.download_updated.emit(item)
        self.history_changed.emit()
        self._schedule_save()

    def _close_file(self, item: DownloadItem):
        if item._file is not None:
            try:
                item._file.close()
            except OSError:
                pass
            item._file = None

    def remove(self, download_id, delete_file: bool = False):
        item = self.downloads.get(download_id)
        if item is None:
            return
        if item.is_active:
            self.cancel(download_id)
        if delete_file:
            try:
                path = Path(item.save_path)
                if path.exists():
                    path.unlink()
            except OSError:
                pass
        self.downloads.pop(download_id, None)
        self.download_removed.emit(item)
        self.history_changed.emit()
        self._schedule_save()

    def clear_history(self):
        stale = [i for i in list(self.downloads.values()) if not i.is_active]
        for item in stale:
            self.downloads.pop(item.id, None)
            self.download_removed.emit(item)
        if stale:
            self.history_changed.emit()
            self._schedule_save()

    def open_file(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        path = Path(item.save_path)
        if not path.exists():
            self.browser.status_label.setText("File no longer exists on disk.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def open_with(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        if sys.platform == "win32":
            subprocess.Popen(["rundll32", "shell32.dll,OpenAs_RunDLLW", item.save_path])

    def show_in_folder(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        path = Path(item.save_path)
        if not path.exists():
            self.browser.status_label.setText("File no longer exists on disk.")
            return
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(path)])
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    def open_download_folder(self):
        directory = self._default_dir()
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(directory)))

    def copy_link(self, download_id):
        item = self.downloads.get(download_id)
        if item is not None:
            QApplication.clipboard().setText(item.url)
            self.browser.status_label.setText("Download link copied.")

    def copy_path(self, download_id):
        item = self.downloads.get(download_id)
        if item is not None:
            QApplication.clipboard().setText(item.save_path)
            self.browser.status_label.setText("File path copied.")

    def get_page_data_json(self) -> str:
        items = sorted(self.downloads.values(),
                       key=lambda i: i.created_at, reverse=True)
        data = []
        for item in items:
            data.append({
                "id": item.id,
                "filename": item.filename,
                "url": item.url,
                "path": item.save_path,
                "mime_type": item.mime_type,
                "total_size": item.total_size,
                "downloaded_size": item.received_size,
                "status": item.state,
                "created_at": item.created_at,
                "completed_at": item.completed_at,
                "error_message": item.error_message,
                "executable": item.executable,
            })
        return json.dumps(data)

    def _schedule_save(self):
        self._save_timer.start()

    def _save_now(self):
        try:
            data = [item.to_dict() for item in self.downloads.values()]
            self.downloads_file.write_text(
                json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print("Could not save download history:", e)

    def _load(self):
        try:
            if self.downloads_file.exists():
                data = json.loads(self.downloads_file.read_text(encoding="utf-8"))
                for entry in data:
                    try:
                        item = DownloadItem.from_dict(self, entry)
                    except Exception:
                        continue
                    self.downloads[item.id] = item
                    self.next_id = max(self.next_id, item.id + 1)
        except Exception as e:
            print("Could not load download history:", e)
