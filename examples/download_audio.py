"""
Download just the audio track as an mp3.

Note: converting audio formats requires ffmpeg on your system PATH.

Run with:
    python examples/download_audio.py <youtube-url>
"""

from __future__ import annotations

import sys

from d3f4ulttube import DownloadError, YouTube


def print_progress(status: dict) -> None:
    if status["status"] == "downloading":
        pct = status.get("_percent_str", "").strip()
        print(f"\rDownloading audio... {pct}", end="", flush=True)
    elif status["status"] == "finished":
        print("\nConverting...")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python download_audio.py <youtube-url>")
        sys.exit(1)

    video = YouTube(sys.argv[1])
    print(f"Extracting audio from: {video.title}")

    try:
        path = video.audio.download("music", on_progress=print_progress)
        print(f"Saved to: {path}")
    except DownloadError as exc:
        print(f"\nAudio download failed: {exc}")
        print("Tip: audio conversion requires ffmpeg to be installed.")


if __name__ == "__main__":
    main()
