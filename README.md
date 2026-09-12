# D3f4ultTube 🐢▶️

A simple, **turtle-module-simple** Python interface for downloading YouTube
videos, audio tracks, and thumbnails — built on top of the excellent
[`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

```python
from d3f4ulttube import YouTube

video = YouTube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

print(video.title)
print(video.author)
print(video.duration)

video.download()
video.download(quality="720p", output="downloads")

video.audio.download("music")
video.thumbnail.save("thumbnail.jpg")
```

No sprawling config, no boilerplate — just an object with properties and
a couple of `.download()` calls, the same way `turtle` gives you a pen
that just moves and draws.

> **⚖️ Use responsibly.** Only download videos you own, that are
> explicitly licensed for download (e.g. Creative Commons), or that
> you otherwise have permission to download. Downloading copyrighted
> content without permission may violate YouTube's Terms of Service
> and copyright law in your jurisdiction. You are responsible for how
> you use this tool.

---

## Features

- 🎯 **Minimal API** — one `YouTube` class, a handful of properties, two
  `.download()` calls.
- 🎬 **Video downloads** with friendly quality selectors (`"highest"`,
  `"720p"`, `"lowest"`, ...).
- 🎵 **Audio-only downloads** via `video.audio.download(...)`.
- 🖼️ **Thumbnail saving** via `video.thumbnail.save(...)`.
- 🖥️ **Optional desktop GUI** (PySide6, with a PySide2/Qt5 fallback) —
  entirely separate from the core library, so the base package stays
  dependency-light.
- 🧯 **Clear exceptions** instead of cryptic tracebacks.
- 🐍 Works anywhere `yt-dlp` works.

---

## Installation

```bash
pip install d3f4ulttube
```

That's it for the core library — it only depends on `yt-dlp`.

### Optional: desktop GUI

```bash
pip install d3f4ulttube[gui]        # PySide6 (Qt6, recommended)
# or
pip install d3f4ulttube[gui-qt5]    # PySide2 (Qt5)
```

> Qt5's official Python binding is distributed under the package name
> **PySide2** — there is no package literally called "PySide5". If you
> specifically need Qt5 bindings, install `d3f4ulttube[gui-qt5]`.

### Optional: merging/converting formats

Downloading video+audio as a single file, or converting extracted audio
to formats like `mp3`, requires [ffmpeg](https://ffmpeg.org/download.html)
to be installed and available on your system `PATH`. Without it, plain
single-stream downloads still work, but merging/re-encoding steps will
fail with a clear error.

---

## Quickstart

```python
from d3f4ulttube import YouTube

video = YouTube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Metadata is fetched lazily and cached the first time you need it
print(video.title)         # "Never Gonna Give You Up"
print(video.author)        # "Rick Astley"
print(video.duration)      # 213 (seconds)
print(video.views)         # e.g. 1_500_000_000
print(video.publish_date)  # "2009-10-25"

# Download the best available quality into the current directory
video.download()

# Or specify quality and output folder
video.download(quality="720p", output="downloads")

# Audio-only, saved as mp3 by default
video.audio.download("music")

# Save just the thumbnail image
video.thumbnail.save("thumbnail.jpg")
```

### Tracking download progress

```python
def show_progress(status):
    if status["status"] == "downloading":
        pct = status.get("_percent_str", "").strip()
        print(f"\rDownloading... {pct}", end="")
    elif status["status"] == "finished":
        print("\nDone!")

video.download(quality="1080p", on_progress=show_progress)
```

### Handling errors

```python
from d3f4ulttube import (
    YouTube,
    InvalidURLError,
    VideoUnavailableError,
    DownloadError,
)

try:
    video = YouTube("https://www.youtube.com/watch?v=does-not-exist")
    print(video.title)
    video.download()
except InvalidURLError:
    print("That doesn't look like a valid video URL.")
except VideoUnavailableError:
    print("This video is private, removed, or otherwise unavailable.")
except DownloadError as exc:
    print(f"Download failed: {exc}")
```

---

## API Reference

### `YouTube(url, *, on_progress=None)`

Represents a single video. Metadata is fetched from YouTube (via
`yt-dlp`) the first time you access a property, then cached.

| Property        | Type            | Description                                  |
|------------------|-----------------|-----------------------------------------------|
| `.title`         | `str`           | Video title                                   |
| `.author`        | `str`           | Channel / uploader name                       |
| `.channel_url`   | `str \| None`   | URL of the uploading channel                  |
| `.duration`      | `int`           | Duration in seconds                           |
| `.views`         | `int`           | View count                                    |
| `.likes`         | `int \| None`   | Like count, if exposed                        |
| `.publish_date`  | `str \| None`   | Upload date as `YYYY-MM-DD`                   |
| `.description`   | `str`           | Full video description                        |
| `.video_id`      | `str`           | The video's YouTube ID                        |
| `.thumbnail_url` | `str \| None`   | Direct URL to the video's thumbnail           |
| `.info`          | `dict`          | The raw metadata dict returned by `yt-dlp`    |
| `.audio`         | `Audio`         | Audio-only download helper (see below)        |
| `.thumbnail`     | `Thumbnail`     | Thumbnail helper (see below)                  |

#### `.download(quality=None, output=".", filename=None, *, on_progress=None) -> str`

Downloads the video (with audio) and returns the saved file path.

- `quality`: `"highest"` (default), `"lowest"`, or a resolution like
  `"1080p"`, `"720p"`, `"480p"`, `"360p"`.
- `output`: destination directory (created automatically).
- `filename`: filename without extension; defaults to the video title.
- `on_progress`: optional callback receiving `yt-dlp` progress dicts.

### `Audio` — `video.audio`

#### `.download(output=".", filename=None, audio_format="mp3", *, on_progress=None) -> str`

Downloads only the audio track, optionally converting it (requires
ffmpeg for non-native formats).

### `Thumbnail` — `video.thumbnail`

- `.url` — direct URL to the thumbnail image.
- `.save(path="thumbnail.jpg") -> str` — downloads and saves the image.

### Exceptions

All exceptions inherit from `D3f4ultTubeError`:

- `InvalidURLError` — the URL is missing, malformed, or unparsable.
- `VideoUnavailableError` — the video is private, removed, or region-locked.
- `DownloadError` — a download or conversion step failed.
- `DependencyError` — an optional dependency (Qt, ffmpeg) is missing.

---

## Desktop GUI

D3f4ultTube ships with an optional, minimal Qt GUI: paste a URL, hit
**Fetch**, pick a quality, choose a folder, and download — with a
progress bar and no scripting required.

```bash
pip install d3f4ulttube[gui]
d3f4ulttube-gui
# or, equivalently:
python -m d3f4ulttube.gui
```

The GUI lives entirely under `d3f4ulttube.gui` and is never imported by
the core library — `pip install d3f4ulttube` alone gives you a fully
working library with zero Qt dependency.

---

## Project structure

```
d3f4ulttube/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── examples/
│   ├── basic_usage.py
│   ├── download_audio.py
│   ├── metadata_and_thumbnail.py
│   └── launch_gui.py
├── src/
│   └── d3f4ulttube/
│       ├── __init__.py
│       ├── core.py          # YouTube class
│       ├── audio.py         # Audio helper
│       ├── thumbnail.py     # Thumbnail helper
│       ├── exceptions.py
│       ├── utils.py
│       └── gui/             # optional PySide6/PySide2 GUI
│           ├── __init__.py
│           ├── app.py
│           └── __main__.py
└── tests/
    ├── test_core.py
    └── test_utils.py
```

---

## Development

```bash
git clone https://github.com/D3F4ULT64/d3f4ulttube.git
cd d3f4ulttube
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,gui]"
pytest
```

Contributions are welcome — please open an issue or pull request.

---

## Disclaimer

This project is an independent wrapper around `yt-dlp` and is not
affiliated with, endorsed by, or sponsored by YouTube or Google.
Downloading videos may be subject to YouTube's Terms of Service and
local copyright law; you are solely responsible for ensuring you have
the right to download and use any content you access with this tool.

## License

MIT — see [LICENSE](LICENSE).
