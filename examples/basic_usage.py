"""
Basic usage: fetch metadata and download a video.

Run with:
    python examples/basic_usage.py <youtube-url>
"""

from __future__ import annotations

import sys

from d3f4ulttube import DownloadError, InvalidURLError, VideoUnavailableError, YouTube


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python basic_usage.py <youtube-url>")
        sys.exit(1)

    url = sys.argv[1]

    try:
        video = YouTube(url)

        print(f"Title:    {video.title}")
        print(f"Author:   {video.author}")
        print(f"Duration: {video.duration}s")
        print(f"Views:    {video.views:,}")

        print("\nDownloading at 720p into ./downloads ...")
        path = video.download(quality="720p", output="downloads")
        print(f"Saved to: {path}")

    except InvalidURLError:
        print("That doesn't look like a valid YouTube URL.")
    except VideoUnavailableError:
        print("This video is private, removed, or otherwise unavailable.")
    except DownloadError as exc:
        print(f"Download failed: {exc}")


if __name__ == "__main__":
    main()
