"""Tests for JSON parsing logic."""

import json
import logging

from instagram_downloader.config import Config
from instagram_downloader.downloader import InstagramDownloader


def _make_logger() -> logging.Logger:
    logger = logging.getLogger("test")
    logger.handlers.clear()
    logger.addHandler(logging.NullHandler())
    return logger


def test_parse_saved_posts(tmp_path):
    payload = {
        "saved_saved_media": [
            {
                "title": "title1",
                "string_map_data": {"Saved on": {"timestamp": 123, "href": "http://x"}},
            }
        ]
    }
    json_path = tmp_path / "saved_posts.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    downloader = InstagramDownloader(Config(), _make_logger())
    items = downloader.parse_json_data(json_path, downloader.MEDIA_CATEGORY_SAVED)

    assert len(items) == 1
    assert items[0].title == "title1"
    assert items[0].timestamp == 123
    assert items[0].url == "http://x"


def test_parse_liked_posts(tmp_path):
    payload = {
        "likes_media_likes": [
            {
                "title": "title2",
                "string_list_data": [{"timestamp": 456, "href": "http://y"}],
            }
        ]
    }
    json_path = tmp_path / "liked_posts.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    downloader = InstagramDownloader(Config(), _make_logger())
    items = downloader.parse_json_data(json_path, downloader.MEDIA_CATEGORY_LIKED)

    assert len(items) == 1
    assert items[0].title == "title2"
    assert items[0].timestamp == 456
    assert items[0].url == "http://y"


def test_parse_own_posts(tmp_path):
    payload = {"posts": [{"title": "title3", "creation_timestamp": 789, "uri": "http://z"}]}
    json_path = tmp_path / "posts.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    downloader = InstagramDownloader(Config(), _make_logger())
    items = downloader.parse_json_data(json_path, downloader.MEDIA_CATEGORY_OWN)

    assert len(items) == 1
    assert items[0].title == "title3"
    assert items[0].timestamp == 789
    assert items[0].url == "http://z"
