"""
d3f4ulttube
~~~~~~~~~~~

A simple, turtle-like Python interface for downloading YouTube videos,
audio tracks, and thumbnails — built on top of yt-dlp.

    from d3f4ulttube import YouTube

    video = YouTube("https://www.youtube.com/watch?v=...")
    print(video.title)
    print(video.author)
    print(video.duration)

    video.download()
    video.download(quality="720p", output="downloads")
    video.audio.download("music")
    video.thumbnail.save("thumbnail.jpg")

Only use this library to download content you own or have explicit
permission to download, in accordance with YouTube's Terms of Service
and applicable copyright law.
"""

from .audio import Audio
from .core import YouTube
from .exceptions import (
    D3f4ultTubeError,
    DependencyError,
    DownloadError,
    InvalidURLError,
    VideoUnavailableError,
)
from .thumbnail import Thumbnail

__version__ = "0.1.0"

__all__ = [
    "YouTube",
    "Audio",
    "Thumbnail",
    "D3f4ultTubeError",
    "DownloadError",
    "InvalidURLError",
    "VideoUnavailableError",
    "DependencyError",
    "__version__",
]
