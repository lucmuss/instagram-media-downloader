# Instagram Media Downloader

Instagram Media Downloader is a CLI tool that downloads saved posts, liked posts, and your own posts from an Instagram data export. It reads JSON data from your export, downloads media via yt-dlp, writes CSV metadata, and stores resume state so you can continue later without re-downloading.

## Features

- Download saved, liked, and own posts
- Separate output folders per category
- Resume support via state files
- CSV metadata export
- Config via CLI, environment variables, or INI file
- Consistent logging to console and optional log files

## Requirements

- Python 3.9+
- yt-dlp available in PATH

## Installation

Install dependencies with uv:

```
just setup
```

Install yt-dlp if needed:

```
sudo apt install yt-dlp
```

Alternatively, install it via uv tool management:

```
uv tool install yt-dlp
```

## Instagram Export Data

Download your Instagram data export in JSON format and place it in a directory. The expected structure is:

```
<DATA_DIR>/<USERNAME>/saved/saved_posts.json
<DATA_DIR>/<USERNAME>/likes/liked_posts.json
<DATA_DIR>/<USERNAME>/posts/posts.json
```

Example:

```
/path/to/instagram-export/data/your_username/saved/saved_posts.json
```

If your export uses different filenames or structure, update the config paths or adapt the code in `src/instagram_downloader/config.py`.

## Quick Start

```
uv run python -m instagram_downloader saved
```

## Configuration

Configuration priority (highest to lowest):

1. CLI arguments
2. Environment variables
3. INI file

### Environment Variables

See `.env.example` for all supported variables. Common settings:

- `INSTAGRAM_USERNAME`
- `DATA_DIR`
- `DOWNLOAD_DIR`
- `STATE_DIR`
- `REQUEST_DELAY`
- `MAX_RETRIES`
- `RETRY_DELAY`
- `TIMEOUT`
- `LOG_LEVEL`
- `CSV_EXPORT`

### INI Configuration

Use `config.example.ini` as a template and pass it via `--config`:

```
uv run python -m instagram_downloader saved --config /path/to/config.ini
```

### CLI Arguments

Run:

```
uv run python -m instagram_downloader --help
```

Key options:

- `--username`
- `--data-dir`
- `--output-dir`
- `--config`
- `--delay`
- `--max-retries`
- `--timeout`
- `--no-csv`
- `--log-level`
- `--log-file`
- `--no-log-file`

## Usage

Commands:

- `saved` downloads saved posts
- `liked` downloads liked posts
- `own` downloads your own posts
- `all` downloads all categories

Examples:

```
uv run python -m instagram_downloader saved
uv run python -m instagram_downloader liked --delay 2.0
uv run python -m instagram_downloader own --output-dir /path/to/output
uv run python -m instagram_downloader all --log-level DEBUG
```

## Output

Downloads are written into category folders under `DOWNLOAD_DIR`:

```
<DOWNLOAD_DIR>/saved/
<DOWNLOAD_DIR>/liked/
<DOWNLOAD_DIR>/own/
```

Resume state is stored under `STATE_DIR`:

```
<STATE_DIR>/saved_downloaded.txt
<STATE_DIR>/liked_downloaded.txt
<STATE_DIR>/own_downloaded.txt
```

CSV metadata is written to the repository root:

```
instagram_saved_metadata.csv
instagram_liked_metadata.csv
instagram_own_metadata.csv
```

## Development

Common tasks:

```
just format
just lint
just typecheck
just test
just check
just ci
just bootstrap
```

The `just ci` target runs lint, typecheck, tests, and build locally.
Bootstrap is centralized in `scripts/bootstrap.sh` and can be run via `just bootstrap`.

## Docker

Build and run the container:

```
just docker-up
```

Stop the container:

```
just docker-down
```

The container does not expose ports because this is a CLI tool. Use `docker exec` to run commands inside the container.

## Release

See `docs/release.md` and `docs/git-workflow.md` for the full checklist and git workflow.

## Troubleshooting

- yt-dlp not found: install yt-dlp and ensure it is in PATH.
- JSON file not found: verify `DATA_DIR` and `INSTAGRAM_USERNAME`.
- Rate limits: increase `REQUEST_DELAY` or retry later.
- Partial downloads: re-run the command to resume using state files.

## Security and Privacy

- Do not commit `.env` files or secrets.
- Use this tool only for data you own or are authorized to download.

## Project Layout

```
./
src/instagram_downloader
scripts
tests
docs
examples
docker
README.md
```

## License

MIT License. See `LICENSE`.
