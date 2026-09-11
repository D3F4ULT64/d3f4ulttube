"""Thumbnail download helper, exposed as `YouTube(...).thumbnail`."""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import TYPE_CHECKING

from .exceptions import D3f4ultTubeError

if TYPE_CHECKING:
    from .core import YouTube


class Thumbnail:
    """
    Thumbnail helper attached to a video, e.g.:

        video = YouTube(url)
        video.thumbnail.save("thumbnail.jpg")
    """

    def __init__(self, video: "YouTube"):
        self._video = video

    @property
    def url(self) -> str:
        """Direct URL of the video's (highest-resolution) thumbnail."""
        thumb_url = self._video.thumbnail_url
        if not thumb_url:
            raise D3f4ultTubeError("No thumbnail is available for this video.")
        return thumb_url

    def save(self, path: str = "thumbnail.jpg") -> str:
        """
        Download and save the video's thumbnail image.

        Args:
            path: File path to save the image to, including extension.

        Returns:
            The path the thumbnail was saved to.
        """
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        try:
            urllib.request.urlretrieve(self.url, path)
        except (urllib.error.URLError, OSError) as exc:
            raise D3f4ultTubeError(f"Failed to save thumbnail: {exc}") from exc

        return path

    def __repr__(self) -> str:
        return f"<Thumbnail of {self._video.url!r}>"
