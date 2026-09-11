# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-09-11

### Added
- Initial release.
- `YouTube` class with lazily-fetched metadata (`title`, `author`,
  `duration`, `views`, `likes`, `publish_date`, `description`,
  `video_id`, `thumbnail_url`, raw `info`).
- `YouTube.download()` with friendly `quality` selectors.
- `Audio` helper (`video.audio.download(...)`) for audio-only downloads.
- `Thumbnail` helper (`video.thumbnail.save(...)`).
- Custom exception hierarchy: `D3f4ultTubeError`, `InvalidURLError`,
  `VideoUnavailableError`, `DownloadError`, `DependencyError`.
- Optional PySide6/PySide2 desktop GUI (`d3f4ulttube-gui`).
- Test suite, examples, and full documentation.
