# -*- coding: utf-8 -*-
"""Tests for configuration handling."""

from instagram_downloader.config import Config


def test_config_env_overrides(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    download_dir = tmp_path / "downloads"
    state_dir = tmp_path / "state"

    monkeypatch.setenv("INSTAGRAM_USERNAME", "testuser")
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.setenv("DOWNLOAD_DIR", str(download_dir))
    monkeypatch.setenv("STATE_DIR", str(state_dir))
    monkeypatch.setenv("REQUEST_DELAY", "2.5")
    monkeypatch.setenv("MAX_RETRIES", "5")
    monkeypatch.setenv("RETRY_DELAY", "4.0")
    monkeypatch.setenv("TIMEOUT", "90")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CSV_EXPORT", "false")

    config = Config()

    assert config.username == "testuser"
    assert config.data_dir == data_dir
    assert config.download_dir == download_dir
    assert config.state_dir == state_dir
    assert config.request_delay == 2.5
    assert config.max_retries == 5
    assert config.retry_delay == 4.0
    assert config.timeout == 90
    assert config.log_level == "DEBUG"
    assert config.csv_export is False


def test_config_apply_overrides(tmp_path):
    config = Config()
    config.apply_overrides(
        username="override",
        data_dir=tmp_path / "data",
        download_dir=tmp_path / "downloads",
        request_delay=3.0,
        max_retries=7,
        timeout=120,
        csv_export=False,
        log_level="WARNING",
    )

    assert config.username == "override"
    assert config.data_dir == tmp_path / "data"
    assert config.download_dir == tmp_path / "downloads"
    assert config.request_delay == 3.0
    assert config.max_retries == 7
    assert config.timeout == 120
    assert config.csv_export is False
    assert config.log_level == "WARNING"


def test_get_data_path(tmp_path):
    config = Config()
    config.apply_overrides(username="user", data_dir=tmp_path)

    assert config.get_data_path("saved") == tmp_path / "user" / "saved" / "saved_posts.json"
    assert config.get_data_path("liked") == tmp_path / "user" / "likes" / "liked_posts.json"
    assert config.get_data_path("own") == tmp_path / "user" / "posts" / "posts.json"
