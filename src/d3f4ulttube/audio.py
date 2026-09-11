"""Audio-only download helper, exposed as `YouTube(...).audio`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from .core import YouTube


class Audio:
    """
    Audio-only helper attached to a video, e.g.:

        video = YouTube(url)
        video.audio.download("music")
    """

    def __init__(self, video: "YouTube"):
        self._video = video

    def download(
        self,
        output: str = ".",
        filename: Optional[str] = None,
        audio_format: str = "mp3",
        *,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> str:
        """
        Download only the audio track of the video.

        Args:
            output: Directory to save the file into. Created if missing.
            filename: Optional filename (without extension). Defaults to
                the video's title.
            audio_format: Target audio codec/container, e.g. "mp3", "m4a",
                "wav", "opus".
            on_progress: Optional progress callback (see `YouTube.download`).

        Returns:
            The path to the downloaded audio file.

        Note:
            Converting to formats like mp3/m4a/wav requires ffmpeg to be
            installed and available on your system PATH. Without ffmpeg,
            yt-dlp will fail to run the conversion step.
        """
        return self._video._run_download(
            format_selector="bestaudio/best",
            output=output,
            filename=filename,
            on_progress=on_progress,
            extract_audio=True,
            audio_format=audio_format,
        )

    def __repr__(self) -> str:
        return f"<Audio of {self._video.url!r}>"
