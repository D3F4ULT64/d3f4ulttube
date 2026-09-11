"""Custom exception types used throughout d3f4ulttube."""

from __future__ import annotations


class D3f4ultTubeError(Exception):
    """Base class for all errors raised by d3f4ulttube."""


class InvalidURLError(D3f4ultTubeError):
    """Raised when a URL is missing, malformed, or cannot be parsed."""


class VideoUnavailableError(D3f4ultTubeError):
    """Raised when a video is private, removed, region-locked, or otherwise unavailable."""


class DownloadError(D3f4ultTubeError):
    """Raised when a video/audio/thumbnail download fails."""


class DependencyError(D3f4ultTubeError):
    """Raised when an optional dependency (e.g. PySide6/PySide2, ffmpeg) is missing."""
