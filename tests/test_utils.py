from __future__ import annotations

import pytest

from d3f4ulttube.utils import build_format_selector, sanitize_filename


def test_sanitize_filename_removes_invalid_chars():
    assert sanitize_filename('Bad:/Name?*.mp4') == "BadName.mp4"


def test_sanitize_filename_empty_falls_back():
    assert sanitize_filename("") == "untitled"


def test_sanitize_filename_truncates():
    long_name = "x" * 500
    assert len(sanitize_filename(long_name)) == 200


def test_build_format_selector_default_is_highest():
    assert build_format_selector(None) == "bestvideo*+bestaudio/best"
    assert build_format_selector("highest") == "bestvideo*+bestaudio/best"


def test_build_format_selector_lowest():
    assert build_format_selector("lowest") == "worstvideo*+worstaudio/worst"


def test_build_format_selector_audio_only():
    assert build_format_selector("audio_only") == "bestaudio/best"


def test_build_format_selector_resolution():
    selector = build_format_selector("720p")
    assert "height<=720" in selector


def test_build_format_selector_invalid_raises():
    with pytest.raises(ValueError):
        build_format_selector("not-a-quality")
