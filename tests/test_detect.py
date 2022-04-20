import sys
from typing import Dict
from unittest import mock
from unittest.mock import ANY

import pytest

import browsers
from browsers import get_available_browsers

"""
These tests assume that Chrome, Firefox, Safari and Microsoft Edge are installed. These are available in Github Actions.
"""


@pytest.mark.parametrize(
    "browser",
    (
        pytest.param("chrome", id="chrome"),
        pytest.param("firefox", id="firefox"),
        pytest.param("safari", id="safari", marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only")),
        pytest.param(
            "msedge", id="msedge", marks=pytest.mark.skipif(sys.platform == "linux", reason="osx-and-windows-only")
        ),
        pytest.param("msie", id="msie", marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only")),
    ),
)
def test_get_available_browsers(browser: str) -> None:
    available_browsers = dict(get_available_browsers())
    assert browser in available_browsers


@pytest.mark.parametrize(
    ("browser", "details"),
    (
        pytest.param(
            "chrome",
            {
                "display_name": "Google Chrome",
                "path": "/Applications/Google Chrome.app",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="chrome-osx",
        ),
        pytest.param(
            "firefox",
            {
                "display_name": "Firefox",
                "path": "/Applications/Firefox.app",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="firefox-osx",
        ),
        pytest.param(
            "safari",
            {
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
                "display_name": "Microsoft Edge",
                "path": "/Applications/Microsoft Edge.app",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
            id="msedge-osx",
        ),
        pytest.param(
            "chrome",
            {
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
                "display_name": "Internet Explorer",
                "path": r"C:\Program Files\Internet Explorer\iexplore.exe",
                "version": ANY,
            },
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
            id="msie-win32",
        ),
    ),
)
def test_get(browser: str, details: Dict) -> None:
    assert browsers.get(browser) == details


@pytest.mark.parametrize(
    "chrome_path",
    (
        pytest.param(
            "/Applications/Google Chrome.app",
            id="osx",
            marks=pytest.mark.skipif(sys.platform != "darwin", reason="osx-only"),
        ),
        pytest.param(
            "/usr/bin/google-chrome-stable",
            id="linux",
            marks=pytest.mark.skipif(sys.platform != "linux", reason="linux-only"),
        ),
        pytest.param(
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            id="windows",
            marks=pytest.mark.skipif(sys.platform != "win32", reason="windows-only"),
        ),
    ),
)
@mock.patch.object(browsers, "_launch")
def test_launch(mock_launch: mock.MagicMock, chrome_path: str) -> None:
    browsers.launch("chrome", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_called_with("chrome", chrome_path, "https://github.com/roniemartinez/browsers", [])


@mock.patch.object(browsers, "_launch")
def test_launch_no_browser(mock_launch: mock.MagicMock) -> None:
    browsers.launch("hello", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_not_called()
