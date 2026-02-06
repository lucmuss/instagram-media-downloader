# -*- coding: utf-8 -*-
"""Logging configuration for Instagram Media Downloader."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Format log records with colors for console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with optional colors."""
        if record.levelname in self.COLORS:
            color_code = self.COLORS[record.levelname]
            reset_code = self.COLORS["RESET"]
            record.levelname = f"{color_code}{record.levelname}{reset_code}"
        return super().format(record)


def setup_logger(
    name: str = "instagram_downloader",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
) -> logging.Logger:
    """Create and configure a logger.

    Args:
        name: Logger name.
        level: Minimum log level.
        log_file: Optional log file path.
        console: Whether to log to stdout.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    logger.handlers.clear()

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_formatter = ColoredFormatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_log_file_path(base_dir: Path, category: Optional[str] = None) -> Path:
    """Generate a log file path with a timestamp."""
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if category:
        log_filename = f"instagram_downloader_{category}_{timestamp}.log"
    else:
        log_filename = f"instagram_downloader_{timestamp}.log"

    return logs_dir / log_filename
