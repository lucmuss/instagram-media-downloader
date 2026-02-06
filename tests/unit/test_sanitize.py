# -*- coding: utf-8 -*-
"""Tests for filename sanitization."""

import logging

from instagram_downloader.config import Config
from instagram_downloader.downloader import InstagramDownloader


def test_sanitize_filename():
    logger = logging.getLogger("test")
    downloader = InstagramDownloader(Config(), logger)

    assert downloader.sanitize_filename("bad:name") == "bad_name"
    assert downloader.sanitize_filename("   ") == "media"
