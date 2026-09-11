"""
Print full metadata for a video and save its thumbnail.

Run with:
    python examples/metadata_and_thumbnail.py <youtube-url>
"""

from __future__ import annotations

import sys

from d3f4ulttube import YouTube


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python metadata_and_thumbnail.py <youtube-url>")
        sys.exit(1)

    video = YouTube(sys.argv[1])

    print(f"Title:        {video.title}")
    print(f"Author:       {video.author}")
    print(f"Channel URL:  {video.channel_url}")
    print(f"Duration:     {video.duration}s")
    print(f"Views:        {video.views:,}")
    print(f"Likes:        {video.likes}")
    print(f"Published:    {video.publish_date}")
    print(f"Video ID:     {video.video_id}")
    print(f"Description:  {video.description[:200]}...")

    thumb_path = video.thumbnail.save("thumbnail.jpg")
    print(f"\nThumbnail saved to: {thumb_path}")


if __name__ == "__main__":
    main()
