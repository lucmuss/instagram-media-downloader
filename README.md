# Instagram Media Downloader v2.0

A **professional** Python CLI tool for downloading Instagram media from your data export.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

✅ **Separate Categories** - Download Saved Posts (Bookmarks), Liked Posts, and own posts
✅ **Professional CLI** - Intuitive command-line interface with many options
✅ **Organized Structure** - Automatic sorting into separate folders (saved/, liked/, own/)
✅ **Configurable** - Via CLI arguments, environment variables, or config file
✅ **Robust Logging** - Colored console output + detailed log files
✅ **Retry Mechanism** - Automatic retry attempts on errors
✅ **Resume Function** - Continue after interruption without re-downloading
✅ **CSV Export** - Detailed metadata for all downloads
✅ **Progress Tracking** - Progress bar with tqdm
✅ **Production-Ready** - Error handling, validation, clean architecture

## Prerequisites

### System Requirements

- **Python** 3.8 or higher
- **yt-dlp** - For Instagram downloads (system package or pip)
- **tqdm** - Python package (installed automatically)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/lucmuss/instagram-media-downloader.git
cd instagram-media-downloader

# 2. Setup with modern toolchain
just setup

# 3. Install yt-dlp (if not already installed)
# This is an external tool required for Instagram downloads.
# Recommended installation via system package manager:
sudo apt install yt-dlp  # For Debian/Ubuntu
# Or via pip (may cause compatibility issues):
# uv run pip install yt-dlp

# 4. Configure via environment variables
# Copy .env.example to .env and fill in the necessary values.
# (Details in "Configuration" section)

# 5. Ready! The tool can now be used:
uv run python -m instagram_downloader --help
```

💡 **Note:** The tool will be available as `instagram-downloader` when the virtual environment is activated.
Alternatively, you can always run it with `uv run python -m instagram_downloader`.

### Development Workflow

```bash
# Setup project
just setup

# Start development environment
just dev

# Format code
just format

# Check code quality
just lint

# Type checking
just typecheck

# Run tests
just test

# Complete quality check
just check

# Clean artifacts
just clean
```

## Configuration

The tool can be configured in three ways (priority: CLI arguments > environment variables > .ini file):

#### 1. Environment Variables (recommended)
Create a `.env` file by copying `.env.example` and adjusting the values. This file should be in the project root and **not committed to Git**.

```bash
# Example .env
INSTAGRAM_USERNAME="my_username"
DATA_DIR="/path/to/instagram-export/data"
DOWNLOAD_DIR="/path/to/output"
REQUEST_DELAY="1.5"
MAX_RETRIES="5"
LOG_LEVEL="DEBUG"
```

#### 2. Configuration File (.ini)
You can also use `config.ini` with `config.example.ini` as template.

```ini
# Example config.ini
[DEFAULT]
username = my_username
data_dir = /path/to/data
download_dir = /path/to/output
```

Use the `--config FILE.ini` option in CLI to load a specific configuration file.

#### 3. CLI Arguments
All configuration options can also be passed directly as command-line arguments (e.g. `--username my_username`). These have the highest priority.

## Quick Start

#### 1. Prepare Instagram Data Export

Download your Instagram data export and ensure it has this structure:

```
instagram-media-downloader/
├── data/
│   └── username/              # Your username (must match INSTAGRAM_USERNAME)
│       ├── saved/
│       │   └── saved_posts.json     # Saved posts (Bookmarks)
│       └── likes/
│           └── liked_posts.json     # Liked posts
```

**Download Instagram data:**
1. Instagram → Settings → Account Center → Your information and permissions
2. "Download information" → Select JSON format
3. Wait for email with download link
4. Extract data into `data/` folder within your project directory

### 2. Use the Tool

```bash
# Download liked posts
uv run python -m instagram_downloader liked

# Download saved posts (Bookmarks)
uv run python -m instagram_downloader saved

# Download everything
uv run python -m instagram_downloader all
```

## Usage

### Basic Syntax

```bash
# Recommended method: Run directly as module
uv run python -m instagram_downloader <command> [options]
```

### Available Commands

| Command | Description |
|---------|-------------|
| `saved` | Downloads saved posts (Bookmarks) |
| `liked` | Downloads liked posts |
| `own` | Downloads own posts |
| `all` | Downloads all three categories |

### CLI Options

#### Configuration

```bash
-u, --username USERNAME        Instagram username
-d, --data-dir PATH           Directory with Instagram export data
-o, --output-dir PATH         Target directory for downloads
-c, --config PATH             Path to configuration file (.ini)
```

#### Download Options

```bash
--delay SECONDS               Delay between downloads (Default: 1.0)
--max-retries N               Max retry attempts (Default: 3)
--timeout SECONDS             Timeout for downloads (Default: 60)
--no-csv                      Disable CSV metadata export
```

#### Logging

```bash
--log-level LEVEL             Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
--log-file PATH               Path to log file
--no-log-file                 Do not create log file (console only)
```

### Examples

#### With custom username

```bash
uv run python -m instagram_downloader liked --username my_username
```

#### With adjusted delay (for rate limits)

```bash
uv run python -m instagram_downloader saved --delay 2.5
```

#### With debug logging

```bash
uv run python -m instagram_downloader all --log-level DEBUG
```

#### With configuration file

```bash
# 1. Copy example configuration
cp config.example.ini config.ini

# 2. Adjust username and paths in config.ini

# 3. Use
uv run python -m instagram_downloader saved --config config.ini
```

#### Custom output directory

```bash
uv run python -m instagram_downloader liked --output-dir /mnt/external-drive/instagram
```

#### Resume downloads

```bash
# Automatically resumes - skips already downloaded files
uv run python -m instagram_downloader liked
```

## Directory Structure

After installation and first use:

```
instagram-media-downloader/
├── instagram_downloader/       # Python package
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                 # CLI interface
│   ├── config.py              # Configuration
│   ├── downloader.py          # Download logic
│   └── logger.py              # Logging
├── data/                      # Instagram export data
│   └── username/
│       ├── saved/
│       ├── likes/
│       └── posts/
├── downloads/                 # Downloaded media
│   ├── saved/                # Saved posts
│   ├── liked/                # Liked posts
│   └── own/                  # Own posts
├── state/                    # Resume state files
│   ├── saved_downloaded.txt
│   ├── liked_downloaded.txt
│   └── own_downloaded.txt
├── logs/                     # Log files
│   └── instagram_downloader_*.log
├── config.example.ini        # Example configuration
├── pyproject.toml            # Project configuration (uv, Ruff)
├── Justfile                  # Task runner
├── .pre-commit-config.yaml   # Pre-commit hooks
├── docker/                   # Docker configuration
│   ├── Dockerfile
│   └── entrypoint.sh
└── README.md                 # This file
```

## CSV Metadata

A CSV file is created for each category:

- `instagram_saved_metadata.csv`
- `instagram_liked_metadata.csv`
- `instagram_own_metadata.csv`

**Format:**

| Column | Description |
|--------|-------------|
| source | Category (saved, liked, own) |
| title | Instagram username of creator |
| timestamp | Unix timestamp |
| datetime | Readable date/time |
| url | Original Instagram URL |
| filename | Local filename |
| media_type | video or image |

## Troubleshooting

### yt-dlp not found

**Problem:** `yt-dlp is not installed!`

**Solution:**
```bash
# System-wide installation (recommended)
sudo apt update
sudo apt install yt-dlp

# Or in virtual environment
uv run pip install yt-dlp

# Verify
yt-dlp --version
```

### Instagram Rate Limits

**Problem:** Many downloads fail

**Solution:** Increase delay:
```bash
uv run python -m instagram_downloader saved --delay 2.5
# or even
uv run python -m instagram_downloader saved --delay 5.0
```

### JSON File Not Found

**Problem:** `JSON file not found`

**Solution:** Check paths and username:
```bash
uv run python -m instagram_downloader liked --data-dir /correct/path/to/data --username your_username

# Or set environment variables
export INSTAGRAM_USERNAME="your_username"
export DATA_DIR="/correct/path/to/data"
uv run python -m instagram_downloader liked
```

### Downloads Fail

**Possible causes:**
- Posts were deleted
- Account is private
- Network issues
- Instagram changes

**Solution:** Check logs in `logs/` directory

### Resume After Interruption

Simply run the same command again:
```bash
uv run python -m instagram_downloader liked
# Automatically skips already downloaded files
# based on state/liked_downloaded.txt
```

## Development

### Setup Development Environment

```bash
# Setup project
just setup

# Start development environment
just dev

# Format code
just format

# Check code quality
just lint

# Type checking
just typecheck

# Run tests
just test

# Complete quality check
just check

# Clean artifacts
just clean
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

## Docker

### Build and Run

```bash
# Build and start container
just docker-up

# Stop container
just docker-down
```

## Notes

⚠️ **Instagram Terms of Service** - Use this tool only for your own data
⚠️ **Rate Limits** - Respect Instagram's server limits
⚠️ **Privacy** - Downloaded media are your personal backups
⚠️ **No Guarantee** - Instagram can change HTML structure anytime

## License

MIT License - For personal use. See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please create a Pull Request or open an Issue.

## Support

For issues please create a GitHub Issue with:
- **Error message** (full stacktrace)
- **Python version:** `python3 --version`
- **yt-dlp version:** `yt-dlp --version`
- **Command used** (e.g. `uv run python -m instagram_downloader liked`)
- **Log output** (from `logs/` directory)
- **Operating system** (Ubuntu, macOS, etc.)

## Changelog

### Version 2.0.0 (2026-02-04)

- ✨ Complete migration to modern toolchain (uv, Ruff, Justfile)
- ✨ Replaced pip/setuptools with uv for 10-100x faster dependency management
- ✨ Replaced Black/Flake8/isort with Ruff for 100x faster linting and formatting
- ✨ Added Justfile for standardized development workflows
- ✨ Added pre-commit hooks with Ruff
- ✨ Added Docker configuration with uv
- ✨ Updated documentation for modern toolchain
- ✨ All texts in English, no special characters

### Version 2.0.0 (2026-01-29)

- ✨ Complete rewrite to professional CLI tool
- ✨ Separate folders for saved/liked/own
- ✨ Configuration system (CLI/ENV/Config-File)
- ✨ Professional logging with colors
- ✨ Retry mechanism with exponential backoff
- ✨ pyproject.toml for modern packaging
- ✨ Comprehensive documentation
- ✨ Production-ready code quality

### Version 1.0.0

- Initial version with basic features

---

**Developed with ❤️ for Instagram collectors**