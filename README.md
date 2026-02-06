# Instagram Media Downloader

Instagram Media Downloader is a CLI tool that downloads saved posts, liked posts, and your own posts from an Instagram data export.

## Requirements

- Python 3.9+
- yt-dlp available in PATH

## Installation

```
just setup
```

Install yt-dlp if needed:

```
sudo apt install yt-dlp
```

## Quick Start

```
uv run python -m instagram_downloader saved
```

## Configuration

Configuration priority:
1. CLI arguments
2. Environment variables
3. INI file

See `docs/configuration.md` for details.

## Usage

See `docs/usage.md` and `examples/basic-usage.md`.

## Project Layout

```
.
src/instagram_downloader
tests
docs
examples
docker
README.md
```

## Development

```
just format
just lint
just typecheck
just test
just ci
```

## Release

See `docs/release.md` and `docs/git-workflow.md`.
