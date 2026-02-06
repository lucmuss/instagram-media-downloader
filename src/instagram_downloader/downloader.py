# -*- coding: utf-8 -*-
"""Download manager for Instagram media."""

import csv
import json
import logging
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tqdm import tqdm

from .config import Config


class MediaItem:
    """Represents a single Instagram media item with metadata."""

    def __init__(self, source: str, title: str, timestamp: int, url: str) -> None:
        """Initialize a media item.

        Args:
            source: Source category (saved, liked, own).
            title: Media title or description.
            timestamp: Unix timestamp.
            url: Instagram URL.
        """
        self.source = source
        self.title = title
        self.timestamp = timestamp
        self.url = url
        self.filename: Optional[str] = None
        self.media_type: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert the item to a CSV-friendly dictionary."""
        return {
            "source": self.source,
            "title": self.title,
            "timestamp": str(self.timestamp),
            "datetime": datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "url": self.url,
            "filename": self.filename or "",
            "media_type": self.media_type or "",
        }


class DownloadStats:
    """Track download statistics."""

    def __init__(self) -> None:
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.total = 0

    def increment_success(self) -> None:
        """Increment successful download count."""
        self.success += 1

    def increment_failed(self) -> None:
        """Increment failed download count."""
        self.failed += 1

    def increment_skipped(self) -> None:
        """Increment skipped download count."""
        self.skipped += 1

    def set_total(self, total: int) -> None:
        """Set the total item count."""
        self.total = total

    def __str__(self) -> str:
        return (
            f"Total: {self.total} | "
            f"Successful: {self.success} | "
            f"Failed: {self.failed} | "
            f"Skipped: {self.skipped}"
        )


class InstagramDownloader:
    """Main class for downloading Instagram media."""

    MEDIA_CATEGORY_SAVED: str = "saved"
    MEDIA_CATEGORY_LIKED: str = "liked"
    MEDIA_CATEGORY_OWN: str = "own"

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        """Initialize the downloader."""
        self.config = config
        self.logger = logger
        self.stats = DownloadStats()

    def check_ytdlp(self) -> bool:
        """Return True if yt-dlp is available in PATH."""
        return shutil.which("yt-dlp") is not None

    def sanitize_filename(self, name: str) -> str:
        """Return a filesystem-safe filename."""
        cleaned = re.sub(r"[\\/*?:\"<>|]", "_", name).strip()
        return cleaned or "media"

    def load_downloaded_state(self, state_file: Path) -> set[str]:
        """Load already downloaded URLs from the state file."""
        if state_file.exists():
            with open(state_file, encoding="utf-8") as handle:
                return {line.strip() for line in handle if line.strip()}
        return set()

    def save_downloaded_state(self, state_file: Path, url: str) -> None:
        """Append a URL to the state file."""
        with open(state_file, "a", encoding="utf-8") as handle:
            handle.write(f"{url}\n")

    def download_with_ytdlp(
        self, url: str, output_template: str, max_retries: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """Download media with yt-dlp and retry on failure."""
        if max_retries is None:
            max_retries = self.config.max_retries

        for attempt in range(max_retries + 1):
            try:
                cmd = [
                    "yt-dlp",
                    "--quiet",
                    "--no-warnings",
                    "--no-progress",
                    "-o",
                    output_template,
                    "--no-playlist",
                    "--format",
                    "best",
                    url,
                ]

                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    check=True,
                )

                base_path = Path(output_template)
                parent_dir = base_path.parent
                name_pattern = base_path.stem

                for ext in [".mp4", ".jpg", ".jpeg", ".png", ".webm", ".mkv"]:
                    potential_file = parent_dir / f"{name_pattern}{ext}"
                    if potential_file.exists():
                        return True, potential_file.name

                self.logger.warning("Download succeeded but output file was not found")
                return False, None

            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.strip() if exc.stderr else "unknown error"
                self.logger.error(
                    "yt-dlp failed (attempt %s/%s): %s", attempt + 1, max_retries + 1, stderr
                )
                if attempt < max_retries:
                    self.logger.warning("Retrying in %s seconds", self.config.retry_delay)
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None
            except subprocess.TimeoutExpired:
                self.logger.warning(
                    "Download timed out (attempt %s/%s)", attempt + 1, max_retries + 1
                )
                if attempt < max_retries:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None
            except Exception as exc:
                self.logger.error(
                    "Unexpected error during download (attempt %s/%s): %s",
                    attempt + 1,
                    max_retries + 1,
                    exc,
                )
                if attempt < max_retries:
                    time.sleep(self.config.retry_delay)
                else:
                    return False, None

        return False, None

    def parse_json_data(self, json_path: Path, category: str) -> List[MediaItem]:
        """Parse JSON export data into MediaItem objects."""
        items: List[MediaItem] = []

        if not json_path.exists():
            self.logger.warning("JSON file not found: %s", json_path)
            return items

        try:
            with open(json_path, encoding="utf-8") as handle:
                data = json.load(handle)

            if category == self.MEDIA_CATEGORY_SAVED:
                items = self._parse_saved_posts(data)
            elif category == self.MEDIA_CATEGORY_LIKED:
                items = self._parse_liked_posts(data)
            elif category == self.MEDIA_CATEGORY_OWN:
                items = self._parse_own_posts(data)
            else:
                self.logger.error("Unknown media category: %s", category)

            self.logger.info("Found %s %s items", len(items), category)

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in file: %s", json_path)
        except Exception as exc:
            self.logger.error("Failed to parse %s: %s", json_path, exc)

        return items

    def _parse_saved_posts(self, data: Dict) -> List[MediaItem]:
        """Parse saved posts from export data."""
        items: List[MediaItem] = []
        try:
            for item in data.get("saved_saved_media", []):
                title = item.get("title", "untitled")
                saved_data = item["string_map_data"]["Saved on"]
                timestamp = saved_data["timestamp"]
                url = saved_data["href"]

                items.append(MediaItem(self.MEDIA_CATEGORY_SAVED, title, timestamp, url))
        except Exception as exc:
            self.logger.error("Failed to parse saved posts: %s", exc)

        return items

    def _parse_liked_posts(self, data: Dict) -> List[MediaItem]:
        """Parse liked posts from export data."""
        items: List[MediaItem] = []
        try:
            for item in data.get("likes_media_likes", []):
                title = item.get("title", "untitled")
                string_list = item.get("string_list_data")
                if string_list:
                    liked_data = string_list[0]
                    timestamp = liked_data["timestamp"]
                    url = liked_data["href"]
                    items.append(MediaItem(self.MEDIA_CATEGORY_LIKED, title, timestamp, url))
        except Exception as exc:
            self.logger.error("Failed to parse liked posts: %s", exc)

        return items

    def _parse_own_posts(self, data: Dict) -> List[MediaItem]:
        """Parse own posts from export data."""
        items: List[MediaItem] = []
        for item in data.get("posts", []):
            title = item.get("title", "untitled")
            timestamp = item.get("creation_timestamp", 0)
            url = item.get("uri", "")

            if url:
                items.append(MediaItem(self.MEDIA_CATEGORY_OWN, title, timestamp, url))

        return items

    def export_to_csv(self, items: List[MediaItem], csv_file: Path) -> None:
        """Export media metadata to CSV."""
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as handle:
                fieldnames = [
                    "source",
                    "title",
                    "timestamp",
                    "datetime",
                    "url",
                    "filename",
                    "media_type",
                ]
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()

                for item in items:
                    writer.writerow(item.to_dict())

            self.logger.info("CSV export saved: %s", csv_file)

        except Exception as exc:
            self.logger.error("CSV export failed: %s", exc)

    def download_category(self, category: str) -> bool:
        """Download all media for a category."""
        self.logger.info("Starting download for category: %s", category)

        json_path = self.config.get_data_path(category)
        download_dir = self.config.get_download_path(category)
        state_file = self.config.get_state_file(category)

        items = self.parse_json_data(json_path, category)

        if not items:
            self.logger.warning("No items found for %s", category)
            return False

        items.sort(key=lambda item: item.timestamp, reverse=True)

        downloaded_urls = self.load_downloaded_state(state_file)
        skipped_items = [item for item in items if item.url in downloaded_urls]
        items_to_download = [item for item in items if item.url not in downloaded_urls]

        self.stats.set_total(len(items))
        self.stats.skipped = len(skipped_items)

        self.logger.info("Already downloaded: %s", len(downloaded_urls))
        self.logger.info("Remaining items to download: %s", len(items_to_download))

        if not items_to_download:
            self.logger.info("All items already downloaded")
            return True

        for item in tqdm(items_to_download, desc=f"Downloading {category}", unit="file"):
            try:
                filename_base = f"{item.timestamp}_{self.sanitize_filename(item.title)}"
                output_template = str(download_dir / filename_base) + ".%(ext)s"

                success, filename = self.download_with_ytdlp(item.url, output_template)

                if success:
                    item.filename = filename
                    item.media_type = (
                        "video"
                        if filename and filename.endswith((".mp4", ".webm", ".mkv"))
                        else "image"
                    )
                    self.save_downloaded_state(state_file, item.url)
                    self.stats.increment_success()
                else:
                    tqdm.write(f"Failed: {item.title[:50]}")
                    self.stats.increment_failed()

                time.sleep(self.config.request_delay)

            except KeyboardInterrupt:
                self.logger.warning("Download interrupted by user")
                raise

            except Exception as exc:
                self.logger.error("Error downloading '%s': %s", item.title[:50], exc, exc_info=True)
                self.stats.increment_failed()

        if self.config.csv_export:
            csv_file = self.config.get_csv_file(category)
            successful_items = [item for item in items if item.filename]
            self.export_to_csv(successful_items, csv_file)

        return True
