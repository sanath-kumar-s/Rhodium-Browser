"""Rhodium download manager.

Central, self-contained download system built on QtWebEngine's
``QWebEngineDownloadRequest``. All download state lives in Python and the
manager is the single authority for initiation, progress, cancellation,
retry and history persistence (SQLite).

The profile's ``downloadRequested`` signal is connected exactly once for the
whole application and dispatched to the live manager, so multiple browser
windows never create duplicate handlers on the shared profile.
"""

import os
import sqlite3
import subprocess
import sys
import time
import weakref
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWidgets import QApplication, QFileDialog

from rhodium.profile_manager import get_web_profile


# ── States ───────────────────────────────────────────────────────────────────
class DownloadState:
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


TERMINAL_STATES = {
    DownloadState.COMPLETED,
    DownloadState.FAILED,
    DownloadState.CANCELLED,
    DownloadState.INTERRUPTED,
}

ACTIVE_STATES = {DownloadState.QUEUED, DownloadState.DOWNLOADING, DownloadState.PAUSED}

RETRYABLE_STATES = {DownloadState.QUEUED} | TERMINAL_STATES

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


# ── Formatting helpers ───────────────────────────────────────────────────────
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


def executable_ext(filename: str) -> bool:
    return Path(filename or "").suffix.lower() in EXECUTABLE_EXTS


def unique_path(directory: Path, filename: str) -> Path:
    filename = (filename or "download").strip() or "download"
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


# ── Item model ───────────────────────────────────────────────────────────────
class DownloadItem(QObject):
    """A single download (web engine or retry-network) tracked by the manager."""

    updated = pyqtSignal()

    def __init__(self, manager, url="", filename="download", save_path="",
                 item_id=0, mime_type="", total_size=-1, engine="webengine"):
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
        self.executable = executable_ext(filename)
        self.engine = engine
        self.request = None
        self.reply = None
        self._file = None
        self._part = None
        self._speed = 0.0
        self._last_bytes = 0
        self._last_time = time.monotonic()

    # -- derived ------------------------------------------------------------
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
        return self.state in ACTIVE_STATES

    def sample_speed(self):
        now = time.monotonic()
        elapsed = now - self._last_time
        if elapsed < 0.05:
            return
        delta = self.received_size - self._last_bytes
        instant = max(0.0, delta / elapsed)
        self._speed = (self._speed * 0.65 + instant * 0.35) if self._speed else instant
        self._last_bytes = self.received_size
        self._last_time = now

    def can_pause(self) -> bool:
        return (self.state == DownloadState.DOWNLOADING
                and self.engine == "webengine" and self.request is not None)

    def can_resume(self) -> bool:
        return (self.state == DownloadState.PAUSED
                and self.engine == "webengine" and self.request is not None)

    def can_retry(self) -> bool:
        return (self.state in RETRYABLE_STATES
                and self.url.startswith(("http://", "https://")))

    # -- serialization ------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "filename": self.filename,
            "save_path": self.save_path,
            "mime_type": self.mime_type,
            "total_size": self.total_size,
            "received_size": self.received_size,
            "status": self.state,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "executable": self.executable,
            "engine": self.engine,
        }

    def to_page_dict(self) -> dict:
        data = self.to_dict()
        data["can_pause"] = self.can_pause()
        data["can_resume"] = self.can_resume()
        data["can_retry"] = self.can_retry()
        data["downloaded_size"] = self.received_size
        data["speed"] = int(self.speed)
        eta = self.eta
        data["eta"] = int(eta) if eta >= 0 else -1
        if data["error_message"] == "":
            data.pop("error_message", None)
        return data


# ── Manager ──────────────────────────────────────────────────────────────────
class DownloadManager(QObject):
    download_added = pyqtSignal(object)
    download_updated = pyqtSignal(object)
    download_removed = pyqtSignal(object)
    history_changed = pyqtSignal()

    # One shared profile connection for the whole application.
    _claimants = []
    _profile_connected = False

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

        self.downloads = {}
        self.next_id = 1
        self.recently_completed_id = None

        self._db_path = Path.home() / ".rhodium" / "downloads.db"
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        self._nam = QNetworkAccessManager(self)
        self._persist_timer = QTimer(self)
        self._persist_timer.setSingleShot(True)
        self._persist_timer.setInterval(400)
        self._persist_timer.timeout.connect(self._persist_now)
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(300)
        self._tick_timer.timeout.connect(self._tick)
        self._tick_timer.start()

        type(self)._claimants.append(weakref.ref(self))
        self._ensure_profile_connected()
        self._load()

    # ------------------------------------------------------------------
    # Profile wiring (connected exactly once)
    # ------------------------------------------------------------------

    @classmethod
    def _live_claimant(cls):
        for ref in cls._claimants:
            mgr = ref()
            if mgr is not None:
                return mgr
        return None

    def _ensure_profile_connected(self):
        cls = type(self)
        if cls._profile_connected:
            return
        try:
            profile = get_web_profile()
            profile.downloadRequested.connect(self._on_profile_download_requested)
            cls._profile_connected = True
        except Exception:
            pass

    def _on_profile_download_requested(self, request):
        mgr = type(self)._live_claimant()
        if mgr is not None:
            mgr.on_download_requested(request)

    # ------------------------------------------------------------------
    # Lookup / convenience
    # ------------------------------------------------------------------

    def default_dir(self) -> Path:
        try:
            value = self.browser.settings_service.get("downloads.directory", str(Path.home() / "Downloads"))
        except Exception:
            value = str(Path.home() / "Downloads")
        return Path(value)

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

    def get_page_data_json(self) -> str:
        import json
        items = sorted(self.downloads.values(),
                       key=lambda i: i.created_at, reverse=True)
        return json.dumps([item.to_page_dict() for item in items])

    # ------------------------------------------------------------------
    # Initiation (web engine)
    # ------------------------------------------------------------------

    def on_download_requested(self, request):
        if not isinstance(request, QWebEngineDownloadRequest):
            return
        if request.state() != QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            return

        target = self._resolve_target(request.suggestedFileName() or "download")
        if target is None:
            request.cancel()
            return

        request.setDownloadDirectory(str(target.parent))
        request.setDownloadFileName(target.name)
        request.accept()

        item = DownloadItem(
            self,
            url=request.url().toString(),
            filename=request.downloadFileName(),
            save_path=str(target),
            item_id=self._allocate_id(),
            mime_type=request.mimeType(),
            total_size=request.totalBytes(),
            engine="webengine",
        )
        item.request = request
        self._register(item)

        request.receivedBytesChanged.connect(lambda it=item: self._sync_progress(it))
        request.totalBytesChanged.connect(lambda it=item: self._sync_total(it))
        request.stateChanged.connect(lambda st, it=item: self._on_webengine_state(it, st))

        self.download_added.emit(item)
        self.download_updated.emit(item)
        self.history_changed.emit()
        self._schedule_persist()

    def _resolve_target(self, suggested):
        try:
            ask = bool(self.browser.settings_service.get("downloads.ask_where", False))
        except Exception:
            ask = False
        directory = self.default_dir()

        if ask:
            start = directory / suggested
            chosen, _ = QFileDialog.getSaveFileName(self.browser, "Save File", str(start))
            if not chosen:
                return None
            chosen_path = Path(chosen)
            if not chosen_path.suffix and Path(suggested).suffix:
                chosen_path = chosen_path.with_suffix(Path(suggested).suffix)
            try:
                chosen_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            try:
                self.browser.settings_service.set("downloads.directory", str(chosen_path.parent))
            except Exception:
                pass
            return unique_path(chosen_path.parent, chosen_path.name)

        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        return unique_path(directory, suggested)

    # ------------------------------------------------------------------
    # Web engine signal sync
    # ------------------------------------------------------------------

    def _allocate_id(self):
        item_id = self.next_id
        self.next_id += 1
        return item_id

    def _register(self, item):
        self.downloads[item.id] = item

    def _sync_progress(self, item):
        if item.request is None:
            return
        item.received_size = item.request.receivedBytes()
        item.sample_speed()
        item.updated.emit()
        self.download_updated.emit(item)

    def _sync_total(self, item):
        if item.request is None:
            return
        total = item.request.totalBytes()
        if total >= 0:
            item.total_size = total
        item.updated.emit()
        self.download_updated.emit(item)

    def _on_webengine_state(self, item, state):
        if item.request is None:
            return
        if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
            item.state = DownloadState.PAUSED if item.request.isPaused() else DownloadState.DOWNLOADING
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self._finish(item, DownloadState.COMPLETED)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self._finish(item, DownloadState.CANCELLED, cleanup=True)
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            reason = item.request.interruptReason()
            reason_name = getattr(reason, "name", "") or ""
            if reason_name == "USER_CANCELED":
                self._finish(item, DownloadState.CANCELLED, cleanup=True)
            else:
                item.error_message = INTERRUPT_MESSAGES.get(
                    reason_name, item.request.interruptReasonString())
                self._finish(item, DownloadState.INTERRUPTED, cleanup=True)
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_persist()

    def _finish(self, item, state, cleanup=False):
        item.state = state
        item.completed_at = datetime.now().isoformat(timespec="seconds")
        if state == DownloadState.COMPLETED:
            if item.total_size > 0:
                item.received_size = item.total_size
            item.error_message = ""
            self.recently_completed_id = item.id
        elif cleanup:
            self._delete_partial(item)
        item.request = None
        item.reply = None
        item._file = None
        item._part = None
        self.history_changed.emit()

    def _delete_partial(self, item):
        try:
            path = Path(item.save_path)
            if path.exists() and item.state != DownloadState.COMPLETED:
                path.unlink()
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Periodic tick (speed sample refresh)
    # ------------------------------------------------------------------

    def _tick(self):
        for item in list(self.downloads.values()):
            if item.state == DownloadState.DOWNLOADING:
                item.sample_speed()
                item.updated.emit()
                self.download_updated.emit(item)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def pause(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.can_pause():
            return
        try:
            item.request.pause()
        except RuntimeError:
            return
        item.state = DownloadState.PAUSED
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_persist()

    def resume(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.can_resume():
            return
        try:
            item.request.resume()
        except RuntimeError:
            return
        item.state = DownloadState.DOWNLOADING
        item.updated.emit()
        self.download_updated.emit(item)

    def cancel(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.is_active:
            return
        if item.engine == "webengine" and item.request is not None:
            try:
                item.request.cancel()
            except RuntimeError:
                pass
        elif item.engine == "network":
            self._abort_network(item, target_state=DownloadState.CANCELLED)
        else:
            self._finish(item, DownloadState.CANCELLED)
        item.updated.emit()
        self.download_updated.emit(item)
        self._schedule_persist()

    def retry(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or not item.can_retry():
            return
        target = Path(item.save_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        item.state = DownloadState.QUEUED
        item.error_message = ""
        item.completed_at = ""
        item.received_size = 0
        item._speed = 0.0
        item._last_bytes = 0
        item._last_time = time.monotonic()
        item.updated.emit()
        self.download_updated.emit(item)
        self._start_network_download(item)

    def remove(self, download_id, delete_file=False):
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
        self._schedule_persist()

    def clear_history(self):
        stale = [item for item in list(self.downloads.values()) if not item.is_active]
        for item in stale:
            self.downloads.pop(item.id, None)
            self.download_removed.emit(item)
        if stale:
            self.history_changed.emit()
            self._schedule_persist()

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    def open_file(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        path = Path(item.save_path)
        if not path.exists():
            self._status("File no longer exists on disk.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def open_with(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        if sys.platform == "win32":
            try:
                subprocess.Popen(["rundll32", "shell32.dll,OpenAs_RunDLLW", item.save_path])
            except OSError:
                pass

    def show_in_folder(self, download_id):
        item = self.downloads.get(download_id)
        if item is None or item.state != DownloadState.COMPLETED:
            return
        path = Path(item.save_path)
        if not path.exists():
            self._status("File no longer exists on disk.")
            return
        if sys.platform == "win32":
            try:
                subprocess.Popen(["explorer", "/select,", str(path)])
            except OSError:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    def open_download_folder(self):
        directory = self.default_dir()
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(directory)))

    def copy_link(self, download_id):
        item = self.downloads.get(download_id)
        if item is not None:
            QApplication.clipboard().setText(item.url)
            self._status("Download link copied.")

    def copy_path(self, download_id):
        item = self.downloads.get(download_id)
        if item is not None:
            QApplication.clipboard().setText(item.save_path)
            self._status("File path copied.")

    def _status(self, text):
        try:
            self.browser.status_label.setText(text)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Retry network download
    # ------------------------------------------------------------------

    def _start_network_download(self, item):
        request = QNetworkRequest(QUrl(item.url))
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute,
                             QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy)
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader,
                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Rhodium")

        reply = self._nam.get(request)
        item.reply = reply
        item.engine = "network"
        item.state = DownloadState.DOWNLOADING
        item.error_message = ""

        part = Path(item.save_path + ".part")
        try:
            part.parent.mkdir(parents=True, exist_ok=True)
            fh = open(part, "wb")
        except OSError as e:
            item.state = DownloadState.FAILED
            item.error_message = f"Cannot write file: {e}"
            item.completed_at = datetime.now().isoformat(timespec="seconds")
            reply.deleteLater()
            item.reply = None
            item.updated.emit()
            self.download_updated.emit(item)
            self._schedule_persist()
            return

        item._file = fh
        item._part = part
        item._last_bytes = 0
        item._last_time = time.monotonic()

        def on_progress(received, total, it=item):
            if total >= 0:
                it.total_size = total
            it.received_size = received
            it.updated.emit()

        reply.downloadProgress.connect(on_progress)

        def on_ready_read(it=item):
            reply_r = it.reply
            if reply_r is None or it._file is None:
                return
            data = bytes(reply_r.readAll())
            if data:
                try:
                    it._file.write(data)
                except OSError as e:
                    it.error_message = f"Cannot write file: {e}"
                    self._abort_network(it, target_state=DownloadState.FAILED)

        reply.readyRead.connect(on_ready_read)
        reply.finished.connect(lambda it=item: self._on_network_finished(it))

    def _abort_network(self, item, target_state):
        if item.reply is not None:
            try:
                item.reply.abort()
            except RuntimeError:
                pass
        self._close_network_file(item, delete_part=True)
        item.reply = None
        item._part = None
        item.state = target_state
        item.completed_at = datetime.now().isoformat(timespec="seconds")
        item.updated.emit()
        self.download_updated.emit(item)
        self.history_changed.emit()
        self._schedule_persist()

    def _close_network_file(self, item, delete_part=False):
        if item._file is not None:
            try:
                item._file.close()
            except OSError:
                pass
            item._file = None
        if delete_part and item._part is not None:
            try:
                part = Path(item._part)
                if part.exists():
                    part.unlink()
            except OSError:
                pass

    def _on_network_finished(self, item):
        reply = item.reply
        if reply is None:
            return
        error = reply.error()
        error_name = getattr(error, "name", "") or ""
        self._close_network_file(item)
        reply.deleteLater()
        item.reply = None

        if item.state in (DownloadState.PAUSED, DownloadState.CANCELLED, DownloadState.FAILED):
            self._schedule_persist()
            return

        if error == QNetworkReply.NetworkError.NoError:
            part = Path(item.save_path + ".part")
            try:
                target = Path(item.save_path)
                if target.exists():
                    target.unlink()
                os.replace(str(part), str(target))
            except OSError as e:
                item.state = DownloadState.FAILED
                item.error_message = f"Cannot finalize file: {e}"
            else:
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

        item._part = None
        item.updated.emit()
        self.download_updated.emit(item)
        self.history_changed.emit()
        self._schedule_persist()

    # ------------------------------------------------------------------
    # Persistence (SQLite)
    # ------------------------------------------------------------------

    def _schedule_persist(self):
        self._persist_timer.start()

    def _connect_db(self):
        return sqlite3.connect(str(self._db_path))

    def _persist_now(self):
        try:
            conn = self._connect_db()
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS downloads (
                        id INTEGER PRIMARY KEY,
                        url TEXT,
                        filename TEXT,
                        save_path TEXT,
                        mime_type TEXT,
                        total_size INTEGER DEFAULT -1,
                        received_size INTEGER DEFAULT 0,
                        status TEXT,
                        error TEXT DEFAULT '',
                        created_at TEXT,
                        completed_at TEXT DEFAULT '',
                        executable INTEGER DEFAULT 0
                    )
                """)
                conn.execute("DELETE FROM downloads")
                rows = [
                    (item.id, item.url, item.filename, item.save_path,
                     item.mime_type, item.total_size, item.received_size,
                     item.state, item.error_message, item.created_at,
                     item.completed_at, int(item.executable))
                    for item in self.downloads.values()
                ]
                conn.executemany("""
                    INSERT INTO downloads
                        (id, url, filename, save_path, mime_type, total_size,
                         received_size, status, error, created_at, completed_at, executable)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rows)
            conn.close()
        except Exception as e:
            print("Could not save download history:", e)

    def _load(self):
        try:
            conn = self._connect_db()
            found = False
            with conn:
                cursor = conn.execute("SELECT * FROM downloads")
                for row in cursor.fetchall():
                    found = True
                    (item_id, url, filename, save_path, mime_type, total_size,
                     received_size, status, error, created_at, completed_at,
                     executable) = row
                    item = DownloadItem(
                        self,
                        url=str(url or ""),
                        filename=str(filename or "download"),
                        save_path=str(save_path or ""),
                        item_id=int(item_id),
                        mime_type=str(mime_type or ""),
                        total_size=int(total_size if total_size is not None else -1),
                    )
                    item.received_size = int(received_size or 0)
                    item.created_at = str(created_at or "")
                    item.completed_at = str(completed_at or "")
                    item.error_message = str(error or "")
                    item.executable = bool(executable) or executable_ext(filename)
                    if status in ACTIVE_STATES:
                        item.state = DownloadState.INTERRUPTED
                        item.error_message = INTERRUPT_MESSAGES["USER_SHUTDOWN"]
                    else:
                        item.state = str(status or DownloadState.INTERRUPTED)
                    self.downloads[item.id] = item
                    self.next_id = max(self.next_id, item.id + 1)
            conn.close()
            if found:
                self.history_changed.emit()
        except Exception as e:
            print("Could not load download history:", e)
