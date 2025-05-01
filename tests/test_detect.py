import os
import subprocess
import sys
import unittest.mock
from typing import Any
from unittest.mock import ANY

import pytest

import browsers

"""
These tests are based on what browsers exists in Github Actions virtual environments.
"""


@pytest.mark.parametrize(
    "browser",
    (
        pytest.param("chrome", id="chrome"),
        pytest.param(
            "chrome-test",
            id="chrome-test",
            marks=pytest.mark.skipif(
                sys.platform != "darwin" or os.getenv("GITHUB_ACTIONS") != "true", reason="github-actions-only"
            ),
        ),
        pytest.param("firefox", id="firefox"),
        pytest.param("safari", id="safari", marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only")),
        pytest.param(
            "msedge", id="msedge", marks=pytest.mark.skipif(sys.platform == "linux", reason="osx-and-windows-only")
        ),
        pytest.param("msie", id="msie", marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only")),
    ),
)
def test_browsers(browser: str) -> None:
    available_browsers = [b["browser_type"] for b in browsers.browsers()]
    assert browser in available_browsers


@pytest.mark.parametrize(
    "naive",
    (
        pytest.param(False, id="non-naive"),
        pytest.param(True, id="naive"),
    ),
)
@pytest.mark.parametrize(
    ("browser", "details"),
    (
        pytest.param(
            "chrome",
            {
                "browser_type": "chrome",
                "display_name": "Google Chrome",
                "path": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="chrome-osx",
        ),
        pytest.param(
            "chrome-test",
            {
                "browser_type": "chrome-test",
                "display_name": "Google Chrome for Testing",
                "path": "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                "version": ANY,
            },
            marks=pytest.mark.skipif(
                sys.platform != "darwin" or os.getenv("GITHUB_ACTIONS") != "true", reason="github-actions-only"
            ),
            id="chrome-test-osx",
        ),
        pytest.param(
            "firefox",
            {
                "browser_type": "firefox",
                "display_name": "Firefox",
                "path": "/Applications/Firefox.app/Contents/MacOS/firefox",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="firefox-osx",
        ),
        pytest.param(
            "safari",
            {
                "browser_type": "safari",
                "display_name": "Safari",
                "path": "/Applications/Safari.app",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="safari-osx",
        ),
        pytest.param(
            "msedge",
            {
                "browser_type": "msedge",
                "display_name": "Microsoft Edge",
                "path": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="msedge-osx",
        ),
        pytest.param(
            "chrome",
            {
                "browser_type": "chrome",
                "display_name": "Google Chrome",
                "path": "/usr/bin/google-chrome-stable",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "linux", reason="linux-only"),
            id="chrome-linux",
        ),
        pytest.param(
            "firefox",
            {
                "browser_type": "firefox",
                "display_name": "Firefox Web Browser",
                "path": "firefox",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "linux", reason="linux-only"),
            id="firefox-linux",
        ),
        pytest.param(
            "chrome",
            {
                "browser_type": "chrome",
                "display_name": "Google Chrome",
                "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
            id="chrome-win32",
        ),
        pytest.param(
            "firefox",
            {
                "browser_type": "firefox",
                "display_name": "Mozilla Firefox",
                "path": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
            id="firefox-win32",
        ),
        pytest.param(
            "msedge",
            {
                "browser_type": "msedge",
                "display_name": "Microsoft Edge",
                "path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
            id="msedge-win32",
        ),
        pytest.param(
            "msie",
            {
                "browser_type": "msie",
                "display_name": "Internet Explorer",
                "path": r"C:\Program Files\Internet Explorer\iexplore.exe",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
            id="msie-win32",
        ),
    ),
)
def test_get(naive: bool, browser: str, details: dict) -> None:
    # if naive, mock subprocess.getoutput else just wrap it
    kwargs: dict[str, Any] = {"return_value": ""} if naive else ({"wraps": subprocess.getoutput})

    with unittest.mock.patch("subprocess.getoutput", **kwargs):
        assert browsers.get(browser) == details
