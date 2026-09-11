"""
A small, beginner-friendly desktop GUI for d3f4ulttube.

Requires PySide6 (preferred) or PySide2 as a fallback:

    pip install d3f4ulttube[gui]       # PySide6
    pip install d3f4ulttube[gui-qt5]   # PySide2

This module is only imported when the GUI is explicitly launched
(`d3f4ulttube-gui` or `python -m d3f4ulttube.gui`) — it is never touched
by the core `d3f4ulttube.YouTube` API.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

from ..core import YouTube
from ..exceptions import D3f4ultTubeError

try:
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    _QT_BINDING = "PySide6"
except ImportError:
    try:
        # Qt5's official Python binding is distributed as "PySide2"
        # (there is no package literally named "PySide5").
        from PySide2.QtCore import Qt, QThread, Signal
        from PySide2.QtWidgets import (
            QApplication,
            QComboBox,
            QFileDialog,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMessageBox,
            QProgressBar,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        _QT_BINDING = "PySide2"
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "The d3f4ulttube GUI requires PySide6 or PySide2. Install one with:\n"
            "  pip install d3f4ulttube[gui]       (PySide6 / Qt6)\n"
            "  pip install d3f4ulttube[gui-qt5]   (PySide2 / Qt5)"
        ) from exc


QUALITY_OPTIONS = ["highest", "1080p", "720p", "480p", "360p", "lowest"]


class DownloadWorker(QThread):
    """Runs a download off the UI thread so the window stays responsive."""

    progress = Signal(dict)
    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, video: YouTube, mode: str, quality: str, output: str):
        super().__init__()
        self.video = video
        self.mode = mode  # "video" or "audio"
        self.quality = quality
        self.output = output

    def run(self) -> None:
        try:
            def hook(status: Dict[str, Any]) -> None:
                self.progress.emit(status)

            if self.mode == "audio":
                path = self.video.audio.download(self.output, on_progress=hook)
            else:
                path = self.video.download(
                    quality=self.quality, output=self.output, on_progress=hook
                )
            self.finished_ok.emit(path)
        except D3f4ultTubeError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"Unexpected error: {exc}")


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("D3f4ultTube")
        self.resize(440, 520)

        self.video: Optional[YouTube] = None
        self.worker: Optional[DownloadWorker] = None

        # -- widgets --
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste a YouTube URL...")
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.clicked.connect(self.fetch_video)

        self.title_label = QLabel("")
        self.title_label.setWordWrap(True)
        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        self.meta_label.setStyleSheet("color: gray;")

        self.quality_box = QComboBox()
        self.quality_box.addItems(QUALITY_OPTIONS)

        self.output_input = QLineEdit(os.getcwd())
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_output)

        self.download_video_btn = QPushButton("Download Video")
        self.download_video_btn.clicked.connect(self.download_video)
        self.download_audio_btn = QPushButton("Download Audio Only")
        self.download_audio_btn.clicked.connect(self.download_audio)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel("Paste a URL and click Fetch to begin.")
        self.status_label.setWordWrap(True)

        self._set_actions_enabled(False)

        # -- layout --
        url_row = QHBoxLayout()
        url_row.addWidget(self.url_input)
        url_row.addWidget(self.fetch_btn)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_input)
        output_row.addWidget(self.browse_btn)

        download_row = QHBoxLayout()
        download_row.addWidget(self.download_video_btn)
        download_row.addWidget(self.download_audio_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(url_row)
        layout.addWidget(self.title_label)
        layout.addWidget(self.meta_label)
        layout.addWidget(QLabel("Quality:"))
        layout.addWidget(self.quality_box)
        layout.addWidget(QLabel("Save to:"))
        layout.addLayout(output_row)
        layout.addLayout(download_row)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

    # -- helpers --

    def _set_actions_enabled(self, enabled: bool) -> None:
        self.quality_box.setEnabled(enabled)
        self.download_video_btn.setEnabled(enabled)
        self.download_audio_btn.setEnabled(enabled)

    # -- slots --

    def fetch_video(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please paste a YouTube URL first.")
            return

        self.status_label.setText("Fetching video info...")
        QApplication.processEvents()

        try:
            self.video = YouTube(url)
            minutes, seconds = divmod(self.video.duration, 60)
            self.title_label.setText(f"<b>{self.video.title}</b>")
            self.meta_label.setText(
                f"{self.video.author}  •  {minutes}:{seconds:02d}  •  "
                f"{self.video.views:,} views"
            )
            self._set_actions_enabled(True)
            self.status_label.setText("Ready to download.")
        except D3f4ultTubeError as exc:
            QMessageBox.critical(self, "Could not load video", str(exc))
            self.status_label.setText("Failed to fetch video info.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Unexpected error", str(exc))
            self.status_label.setText("Failed to fetch video info.")

    def browse_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Choose a folder", self.output_input.text()
        )
        if directory:
            self.output_input.setText(directory)

    def download_video(self) -> None:
        self._start_download(mode="video")

    def download_audio(self) -> None:
        self._start_download(mode="audio")

    def _start_download(self, mode: str) -> None:
        if not self.video:
            return

        self._set_actions_enabled(False)
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading...")

        self.worker = DownloadWorker(
            self.video,
            mode=mode,
            quality=self.quality_box.currentText(),
            output=self.output_input.text().strip() or ".",
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_ok.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_progress(self, status: Dict[str, Any]) -> None:
        if status.get("status") == "downloading":
            total = status.get("total_bytes") or status.get("total_bytes_estimate")
            downloaded = status.get("downloaded_bytes", 0)
            if total:
                self.progress_bar.setValue(int(downloaded / total * 100))

    def on_finished(self, path: str) -> None:
        self.progress_bar.setValue(100)
        self.status_label.setText(f"Done! Saved to: {path}")
        self._set_actions_enabled(True)
        self.fetch_btn.setEnabled(True)

    def on_failed(self, message: str) -> None:
        self.status_label.setText("Download failed.")
        QMessageBox.critical(self, "Download failed", message)
        self._set_actions_enabled(True)
        self.fetch_btn.setEnabled(True)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # PySide6 uses exec(); PySide2 uses exec_().
    run = getattr(app, "exec", None) or app.exec_
    sys.exit(run())


if __name__ == "__main__":
    main()
