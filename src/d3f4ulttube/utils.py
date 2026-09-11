"""Small internal helpers used by the core library."""

from __future__ import annotations

import re

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """
    Strip characters that are invalid in filenames on Windows/macOS/Linux.

    Falls back to "untitled" if the result would be empty.
    """
    if not name:
        return "untitled"
    cleaned = _INVALID_FILENAME_CHARS.sub("", name).strip().strip(".")
    cleaned = cleaned or "untitled"
    return cleaned[:max_length]


def build_format_selector(quality: str | None) -> str:
    """
    Translate a beginner-friendly quality string into a yt-dlp format selector.

    Accepted values:
        None / "highest"  -> best available video+audio (default)
        "lowest"           -> smallest available video+audio
        "audio_only"       -> best available audio stream only
        "<N>p" (e.g. "720p", "1080p", "480p") -> best stream at or below N pixels tall

    Raises:
        ValueError: if `quality` doesn't match any recognized pattern.
    """
    if not quality or quality == "highest":
        return "bestvideo*+bestaudio/best"
    if quality == "lowest":
        return "worstvideo*+worstaudio/worst"
    if quality == "audio_only":
        return "bestaudio/best"

    match = re.fullmatch(r"(\d{3,4})p", quality.strip().lower())
    if not match:
        raise ValueError(
            f"Unrecognized quality {quality!r}. Use 'highest', 'lowest', "
            f"'audio_only', or a resolution like '720p'."
        )
    height = match.group(1)
    return f"bestvideo*[height<={height}]+bestaudio/best[height<={height}]"
