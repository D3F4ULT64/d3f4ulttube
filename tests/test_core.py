from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from d3f4ulttube import YouTube
from d3f4ulttube.exceptions import InvalidURLError, VideoUnavailableError

SAMPLE_INFO = {
    "id": "abc123",
    "title": "Sample Video",
    "uploader": "Sample Channel",
    "duration": 125,
    "view_count": 1000,
    "like_count": 50,
    "upload_date": "20240115",
    "description": "A sample description.",
    "thumbnail": "https://example.com/thumb.jpg",
}


def _mock_ydl(info=None):
    mock_ydl = MagicMock()
    mock_ydl.__enter__.return_value = mock_ydl
    mock_ydl.extract_info.return_value = info
    return mock_ydl


def test_empty_url_raises_invalid_url_error():
    with pytest.raises(InvalidURLError):
        YouTube("")


def test_non_string_url_raises_invalid_url_error():
    with pytest.raises(InvalidURLError):
        YouTube(None)  # type: ignore[arg-type]


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_metadata_properties(mock_ydl_cls):
    mock_ydl_cls.return_value = _mock_ydl(info=SAMPLE_INFO)
    video = YouTube("https://www.youtube.com/watch?v=abc123")

    assert video.title == "Sample Video"
    assert video.author == "Sample Channel"
    assert video.duration == 125
    assert video.views == 1000
    assert video.likes == 50
    assert video.publish_date == "2024-01-15"
    assert video.video_id == "abc123"
    assert video.thumbnail_url == "https://example.com/thumb.jpg"
    assert "sample description" in video.description.lower()


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_info_is_fetched_once_and_cached(mock_ydl_cls):
    mock_instance = _mock_ydl(info=SAMPLE_INFO)
    mock_ydl_cls.return_value = mock_instance
    video = YouTube("https://www.youtube.com/watch?v=abc123")

    _ = video.title
    _ = video.author
    _ = video.duration

    assert mock_instance.extract_info.call_count == 1


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_no_info_raises_video_unavailable(mock_ydl_cls):
    mock_ydl_cls.return_value = _mock_ydl(info=None)
    video = YouTube("https://www.youtube.com/watch?v=missing")

    with pytest.raises(VideoUnavailableError):
        _ = video.title


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_repr_includes_title_and_author(mock_ydl_cls):
    mock_ydl_cls.return_value = _mock_ydl(info=SAMPLE_INFO)
    video = YouTube("https://www.youtube.com/watch?v=abc123")

    assert "Sample Video" in repr(video)
    assert "Sample Channel" in repr(video)


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_download_creates_output_dir_and_calls_ydl(mock_ydl_cls, tmp_path):
    info_ydl = _mock_ydl(info=SAMPLE_INFO)
    download_ydl = MagicMock()
    download_ydl.__enter__.return_value = download_ydl
    mock_ydl_cls.side_effect = [info_ydl, download_ydl]

    video = YouTube("https://www.youtube.com/watch?v=abc123")
    _ = video.title  # triggers metadata fetch (first YoutubeDL instance)

    output_dir = tmp_path / "out"
    video.download(quality="720p", output=str(output_dir))

    assert os.path.isdir(output_dir)
    download_ydl.download.assert_called_once_with(
        ["https://www.youtube.com/watch?v=abc123"]
    )

    download_opts = mock_ydl_cls.call_args_list[1][0][0]
    assert "height<=720" in download_opts["format"]
    assert str(output_dir) in download_opts["outtmpl"]


@patch("d3f4ulttube.core.yt_dlp.YoutubeDL")
def test_audio_download_sets_extract_audio_postprocessor(mock_ydl_cls, tmp_path):
    info_ydl = _mock_ydl(info=SAMPLE_INFO)
    download_ydl = MagicMock()
    download_ydl.__enter__.return_value = download_ydl
    mock_ydl_cls.side_effect = [info_ydl, download_ydl]

    video = YouTube("https://www.youtube.com/watch?v=abc123")
    _ = video.title

    output_dir = tmp_path / "music"
    video.audio.download(str(output_dir))

    download_opts = mock_ydl_cls.call_args_list[1][0][0]
    assert download_opts["format"] == "bestaudio/best"
    assert download_opts["postprocessors"][0]["key"] == "FFmpegExtractAudio"
    assert download_opts["postprocessors"][0]["preferredcodec"] == "mp3"
