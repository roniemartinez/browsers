import os
import sys
from unittest import mock

import pytest

import browsers

"""
These tests are based on what browsers exists in Github Actions virtual environments.
"""


@pytest.mark.parametrize(
    "chrome_path",
    (
        pytest.param(
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
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
    mock_launch.assert_called_with("chrome", chrome_path, [], "https://github.com/roniemartinez/browsers")


@pytest.mark.skipif(sys.platform != "darwin" or os.getenv("GITHUB_ACTIONS") != "true", reason="github-actions-only")
@mock.patch.object(browsers, "_launch")
def test_launch_chrome_test(mock_launch: mock.MagicMock) -> None:
    browsers.launch("chrome-test", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_called_with(
        "chrome-test",
        "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        [],
        "https://github.com/roniemartinez/browsers",
    )


@mock.patch.object(browsers, "_launch")
def test_launch_no_browser(mock_launch: mock.MagicMock) -> None:
    browsers.launch("hello", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_not_called()
