# -*- coding: utf-8 -*-
"""CLI entrypoint for Instagram Media Downloader."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .config import Config
from .downloader import InstagramDownloader
from .logger import get_log_file_path, setup_logger


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="instagram-downloader",
        description="Instagram Media Downloader - download media from your export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  instagram-downloader saved\n"
            "  instagram-downloader liked\n"
            "  instagram-downloader own\n"
            "  instagram-downloader all\n"
            "  instagram-downloader saved --username my_user --delay 2.0\n"
            "  instagram-downloader liked --log-level DEBUG\n\n"
            "Environment variables (see .env.example):\n"
            "  INSTAGRAM_USERNAME  - Instagram username\n"
            "  DATA_DIR           - Directory with Instagram export data\n"
            "  DOWNLOAD_DIR       - Target directory for downloads\n"
            "  REQUEST_DELAY      - Delay between requests (seconds)\n"
            "  MAX_RETRIES        - Max retry attempts\n"
            "  LOG_LEVEL          - Log level (DEBUG, INFO, WARNING, ERROR)\n"
        ),
    )

    parser.add_argument(
        "command",
        choices=["saved", "liked", "own", "all"],
        help="Which media to download",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    config_group = parser.add_argument_group("Configuration")

    config_group.add_argument(
        "-u", "--username", type=str, help="Instagram username (overrides INSTAGRAM_USERNAME)"
    )

    config_group.add_argument("-d", "--data-dir", type=Path, help="Export data directory")

    config_group.add_argument("-o", "--output-dir", type=Path, help="Download output directory")

    config_group.add_argument("-c", "--config", type=Path, help="Path to INI config file")

    download_group = parser.add_argument_group("Download")

    download_group.add_argument(
        "--delay", type=float, help="Delay between downloads in seconds (default: 1.0)"
    )

    download_group.add_argument(
        "--max-retries", type=int, help="Maximum retry attempts (default: 3)"
    )

    download_group.add_argument(
        "--timeout", type=int, help="Timeout per download in seconds (default: 60)"
    )

    download_group.add_argument("--no-csv", action="store_true", help="Disable CSV metadata export")

    log_group = parser.add_argument_group("Logging")

    log_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level (default: INFO)",
    )

    log_group.add_argument("--log-file", type=Path, help="Path to log file")

    log_group.add_argument("--no-log-file", action="store_true", help="Disable log file")

    return parser


def apply_cli_args_to_config(config: Config, args: argparse.Namespace) -> None:
    """Apply CLI arguments to configuration."""
    config.apply_overrides(
        username=args.username,
        data_dir=args.data_dir,
        download_dir=args.output_dir,
        request_delay=args.delay,
        max_retries=args.max_retries,
        timeout=args.timeout,
        csv_export=False if args.no_csv else None,
        log_level=args.log_level,
    )


def print_banner() -> None:
    """Print a simple banner with version information."""
    print("=" * 70)
    print("INSTAGRAM MEDIA DOWNLOADER")
    print(f"Version {__version__}")
    print("=" * 70)
    print()


def print_summary(downloader: InstagramDownloader, download_dir: Path) -> None:
    """Print a summary of download results."""
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Successful:  {downloader.stats.success}")
    print(f"Failed:      {downloader.stats.failed}")
    print(f"Skipped:     {downloader.stats.skipped}")
    print(f"Output dir:  {download_dir}")
    print("=" * 70)

    if downloader.stats.failed > 0:
        print("\nNotes:")
        print("  - Deleted posts cannot be downloaded")
        print("  - Private accounts may require cookies")
        print("  - If rate limited, retry later")


def main(argv: Optional[List[str]] = None) -> None:
    """Main CLI entrypoint."""
    parser = create_parser()
    args = parser.parse_args(argv)

    logger = setup_logger()

    try:
        print_banner()

        config_file = args.config if args.config else None
        config = Config(config_file)
        apply_cli_args_to_config(config, args)

        log_file = None
        if not args.no_log_file:
            log_file = args.log_file or get_log_file_path(config.base_dir, args.command)

        logger = setup_logger(level=config.log_level, log_file=log_file, console=True)

        logger.info("Instagram Media Downloader v%s started", __version__)
        logger.info("Command: %s", args.command)
        logger.info("Username: %s", config.username)

        downloader = InstagramDownloader(config, logger)

        if not downloader.check_ytdlp():
            logger.critical("yt-dlp is not installed or not in PATH")
            print("\nERROR: yt-dlp is not installed or not in PATH")
            print("\nInstallation:")
            print("  sudo apt install yt-dlp")
            print("  # or via pip:")
            print("  uv run pip install yt-dlp")
            sys.exit(1)

        logger.info("yt-dlp detected")

        categories: List[str]
        if args.command == "all":
            categories = [
                downloader.MEDIA_CATEGORY_SAVED,
                downloader.MEDIA_CATEGORY_LIKED,
                downloader.MEDIA_CATEGORY_OWN,
            ]
        else:
            categories = [args.command]

        for category in categories:
            try:
                logger.info("=" * 50)
                logger.info("Category: %s", category.upper())
                logger.info("=" * 50)

                downloader.download_category(category)

                display_download_dir = config.get_download_path(category)
                print_summary(downloader, display_download_dir)

                if len(categories) > 1:
                    downloader.stats = type(downloader.stats)()

            except KeyboardInterrupt:
                logger.warning("Download interrupted by user for category %s", category)
                print("\nDownload can be resumed by re-running the command")
                sys.exit(0)

            except Exception as exc:  # pragma: no cover - guard for unexpected errors
                logger.error("Error in category %s: %s", category, exc, exc_info=True)
                print(f"\nERROR in category '{category}': {exc}")
                continue

        logger.info("All downloads processed")
        print("\nDone. All downloads processed.")

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("\nProgram interrupted by user")
        sys.exit(0)

    except Exception as exc:  # pragma: no cover - guard for unexpected errors
        logger.critical("Fatal error: %s", exc, exc_info=True)
        print(f"\nFATAL ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
