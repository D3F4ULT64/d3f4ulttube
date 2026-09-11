"""Core YouTube video wrapper — the main entry point of d3f4ulttube."""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, Optional

from .exceptions import (
    D3f4ultTubeError,
    DownloadError,
    InvalidURLError,
    VideoUnavailableError,
)
from .utils import build_format_selector, sanitize_filename

try:
    import yt_dlp
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "d3f4ulttube requires 'yt-dlp'. It should have been installed "
        "automatically with 'pip install d3f4ulttube'. Try: pip install yt-dlp"
    ) from exc


ProgressHook = Callable[[Dict[str, Any]], None]


class YouTube:
    """
    A simple, turtle-like interface to a single YouTube video.

    Metadata is fetched lazily the first time you access a property like
    `.title`, and cached for the lifetime of the object.

    Example:
        >>> video = YouTube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        >>> print(video.title)
        >>> video.download(quality="720p", output="downloads")
        >>> video.audio.download("music")
        >>> video.thumbnail.save("thumbnail.jpg")

    Only download content you own the rights to, or have explicit
    permission to download, in line with YouTube's Terms of Service
    and applicable copyright law.
    """

    def __init__(self, url: str, *, on_progress: Optional[ProgressHook] = None):
        if not url or not isinstance(url, str):
            raise InvalidURLError("A non-empty video URL string is required.")

        self.url = url
        self._on_progress = on_progress
        self._info: Optional[Dict[str, Any]] = None

        # Sub-helpers, mirroring the video's own lifecycle.
        from .audio import Audio  # local import avoids a circular import
        from .thumbnail import Thumbnail

        self.audio = Audio(self)
        self.thumbnail = Thumbnail(self)

    # -- internal helpers -----------------------------------------------

    @staticmethod
    def _base_opts() -> dict:
        return {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

    def _fetch_info(self) -> dict:
        if self._info is not None:
            return self._info

        try:
            with yt_dlp.YoutubeDL(self._base_opts()) as ydl:
                info = ydl.extract_info(self.url, download=False)
        except yt_dlp.utils.DownloadError as exc:
            message = str(exc)
            lowered = message.lower()
            if "private" in lowered or "unavailable" in lowered or "removed" in lowered:
                raise VideoUnavailableError(
                    f"This video is unavailable, private, or has been removed: {self.url}"
                ) from exc
            raise InvalidURLError(
                f"Could not read video info for {self.url!r}: {message}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 - surface any unexpected failure clearly
            raise D3f4ultTubeError(
                f"Unexpected error while fetching video info: {exc}"
            ) from exc

        if not info:
            raise VideoUnavailableError(f"No data returned for {self.url}")

        self._info = info
        return info

    @property
    def info(self) -> dict:
        """The raw metadata dictionary as returned by yt-dlp."""
        return self._fetch_info()

    # -- metadata ---------------------------------------------------------

    @property
    def title(self) -> str:
        return self.info.get("title", "Unknown title")

    @property
    def author(self) -> str:
        return self.info.get("uploader") or self.info.get("channel") or "Unknown author"

    @property
    def channel_url(self) -> Optional[str]:
        return self.info.get("channel_url") or self.info.get("uploader_url")

    @property
    def duration(self) -> int:
        """Duration of the video in seconds."""
        return int(self.info.get("duration") or 0)

    @property
    def views(self) -> int:
        return int(self.info.get("view_count") or 0)

    @property
    def likes(self) -> Optional[int]:
        return self.info.get("like_count")

    @property
    def publish_date(self) -> Optional[str]:
        """Upload date formatted as YYYY-MM-DD, if available."""
        date = self.info.get("upload_date")
        if date and len(date) == 8:
            return f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
        return date

    @property
    def description(self) -> str:
        return self.info.get("description", "")

    @property
    def video_id(self) -> str:
        return self.info.get("id", "")

    @property
    def thumbnail_url(self) -> Optional[str]:
        return self.info.get("thumbnail")

    def __repr__(self) -> str:
        return f"<YouTube title={self.title!r} author={self.author!r}>"

    # -- downloading ------------------------------------------------------

    def download(
        self,
        quality: Optional[str] = None,
        output: str = ".",
        filename: Optional[str] = None,
        *,
        on_progress: Optional[ProgressHook] = None,
    ) -> str:
        """
        Download the video, with audio, to disk.

        Args:
            quality: "highest" (default), "lowest", or a resolution such
                as "1080p", "720p", "480p", "360p".
            output: Directory to save the file into. Created if it
                doesn't exist.
            filename: Optional filename (without extension). Defaults to
                a filesystem-safe version of the video title.
            on_progress: Optional callback receiving yt-dlp progress
                dictionaries (status, downloaded_bytes, total_bytes, ...).

        Returns:
            The path to the downloaded file.

        Raises:
            DownloadError: if the download fails.
            VideoUnavailableError: if the video can't be accessed.

        Note:
            Merging separate video/audio streams into one file requires
            ffmpeg to be installed and available on your system PATH.
        """
        return self._run_download(
            format_selector=build_format_selector(quality),
            output=output,
            filename=filename,
            on_progress=on_progress,
            extract_audio=False,
        )

    def _run_download(
        self,
        *,
        format_selector: str,
        output: str,
        filename: Optional[str],
        on_progress: Optional[ProgressHook],
        extract_audio: bool,
        audio_format: str = "mp3",
    ) -> str:
        os.makedirs(output, exist_ok=True)
        name = sanitize_filename(filename or self.title)
        outtmpl = os.path.join(output, f"{name}.%(ext)s")

        hook = on_progress or self._on_progress
        downloaded: Dict[str, str] = {}

        def _hook(status: Dict[str, Any]) -> None:
            if status.get("status") == "finished":
                downloaded["path"] = status.get("filename", "")
            if hook:
                hook(status)

        opts = self._base_opts()
        opts.update(
            {
                "format": format_selector,
                "outtmpl": outtmpl,
                "progress_hooks": [_hook],
            }
        )

        if extract_audio:
            opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": audio_format}
            ]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
        except yt_dlp.utils.DownloadError as exc:
            raise DownloadError(f"Failed to download from {self.url}: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise DownloadError(f"Unexpected error during download: {exc}") from exc

        path = downloaded.get("path", "")
        if extract_audio and path:
            base, _ = os.path.splitext(path)
            converted = f"{base}.{audio_format}"
            if os.path.exists(converted):
                path = converted
        return path or outtmpl
