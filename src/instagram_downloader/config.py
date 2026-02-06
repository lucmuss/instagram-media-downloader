# -*- coding: utf-8 -*-
"""Configuration management for Instagram Media Downloader."""

import configparser
import os
from pathlib import Path
from typing import Optional, Union, cast

from dotenv import load_dotenv

ConfigValue = Union[str, int, float, bool]


class Config:
    """Central configuration object."""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """Initialize configuration.

        Args:
            config_file: Optional path to an INI configuration file.
        """
        load_dotenv()
        self.base_dir = Path(__file__).resolve().parents[2]

        self._defaults: dict[str, ConfigValue] = {
            "username": os.getenv("INSTAGRAM_USERNAME", "username"),
            "data_dir": os.getenv("DATA_DIR", str(self.base_dir / "data")),
            "download_dir": os.getenv("DOWNLOAD_DIR", str(self.base_dir / "downloads")),
            "state_dir": os.getenv("STATE_DIR", str(self.base_dir / "state")),
            "request_delay": float(os.getenv("REQUEST_DELAY", "1.0")),
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("RETRY_DELAY", "5.0")),
            "timeout": int(os.getenv("TIMEOUT", "60")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "csv_export": os.getenv("CSV_EXPORT", "true").lower() == "true",
        }

        if config_file and config_file.exists():
            self._load_config_file(config_file)

    def _load_config_file(self, config_file: Path) -> None:
        """Load settings from an INI file.

        Args:
            config_file: Path to the INI configuration file.
        """
        parser = configparser.ConfigParser()
        parser.read(config_file)

        if "DEFAULT" in parser:
            for key, value in parser["DEFAULT"].items():
                if key in self._defaults:
                    default_type = type(self._defaults[key])
                    if default_type is bool:
                        self._defaults[key] = value.lower() == "true"
                    elif default_type is int:
                        self._defaults[key] = int(value)
                    elif default_type is float:
                        self._defaults[key] = float(value)
                    else:
                        self._defaults[key] = value

    def apply_overrides(self, **overrides: Optional[Union[ConfigValue, Path]]) -> None:
        """Apply runtime overrides from CLI arguments.

        Args:
            overrides: Key-value overrides matching configuration keys.
        """
        for key, value in overrides.items():
            if value is None:
                continue
            if key not in self._defaults:
                raise KeyError(f"Unknown configuration key: {key}")
            if isinstance(value, Path):
                self._defaults[key] = str(value)
            else:
                self._defaults[key] = value

    @property
    def username(self) -> str:
        """Instagram username."""
        return cast(str, self._defaults["username"])

    @property
    def data_dir(self) -> Path:
        """Directory containing the Instagram export data."""
        return Path(cast(str, self._defaults["data_dir"]))

    @property
    def download_dir(self) -> Path:
        """Target directory for downloaded media."""
        return Path(cast(str, self._defaults["download_dir"]))

    @property
    def state_dir(self) -> Path:
        """Directory for download state files."""
        return Path(cast(str, self._defaults["state_dir"]))

    @property
    def request_delay(self) -> float:
        """Delay between downloads in seconds."""
        return cast(float, self._defaults["request_delay"])

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        return cast(int, self._defaults["max_retries"])

    @property
    def retry_delay(self) -> float:
        """Delay between retries in seconds."""
        return cast(float, self._defaults["retry_delay"])

    @property
    def timeout(self) -> int:
        """Timeout for a single download operation in seconds."""
        return cast(int, self._defaults["timeout"])

    @property
    def log_level(self) -> str:
        """Configured log level (for example, INFO or DEBUG)."""
        return cast(str, self._defaults["log_level"])

    @property
    def csv_export(self) -> bool:
        """Whether CSV metadata export is enabled."""
        return cast(bool, self._defaults["csv_export"])

    def get_data_path(self, category: str) -> Path:
        """Return the JSON data path for a category.

        Args:
            category: Media category (saved, liked, own).

        Raises:
            ValueError: If the category is unknown.
        """
        user_data_dir = self.data_dir / self.username

        if category == "saved":
            return user_data_dir / "saved" / "saved_posts.json"
        if category == "liked":
            return user_data_dir / "likes" / "liked_posts.json"
        if category == "own":
            return user_data_dir / "posts" / "posts.json"
        raise ValueError(f"Unknown category: {category}")

    def get_download_path(self, category: str) -> Path:
        """Return the download directory for a category, creating it if needed."""
        download_path = self.download_dir / category
        download_path.mkdir(parents=True, exist_ok=True)
        return download_path

    def get_state_file(self, category: str) -> Path:
        """Return the state file path for a category and ensure the directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        return self.state_dir / f"{category}_downloaded.txt"

    def get_csv_file(self, category: str) -> Path:
        """Return the CSV export file path for a category."""
        return self.base_dir / f"instagram_{category}_metadata.csv"
