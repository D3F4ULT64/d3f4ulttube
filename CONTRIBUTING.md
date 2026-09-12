# Contributing to D3f4ultTube

Thanks for considering a contribution! 🐢

## Getting set up

```bash
git clone https://github.com/D3F4ULT64/d3f4ulttube.git
cd d3f4ulttube
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,gui]"
pytest
```

## Guidelines

- Keep the core `d3f4ulttube` package free of GUI (Qt) dependencies —
  anything Qt-related belongs under `d3f4ulttube/gui/`.
- Favor small, focused pull requests over large ones.
- Add or update tests for any behavior change (tests use mocks and
  don't hit the network).
- Run `pytest` before opening a PR.
- Follow the existing docstring style — every public method/property
  should be documented.

## Reporting bugs / requesting features

Please open a GitHub issue with:
- What you expected to happen.
- What actually happened (include the full traceback if there's an error).
- Your Python version and OS.
- A minimal code snippet that reproduces the issue, if applicable.

## Responsible use

This project only wraps `yt-dlp`'s public API to fetch metadata and
download content. Please keep contributions focused on making that
wrapper simpler and more reliable — not on circumventing platform
protections or facilitating unauthorized redistribution of content.
