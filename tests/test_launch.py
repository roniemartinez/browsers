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


@pytest.mark.parametrize(
    "args, url, expected_command",
    (
        pytest.param(
            ["--private-window"],
            "https://example.com",
            ["/usr/bin/firefox", "--private-window", "https://example.com"],
            id="private-window-with-url",
        ),
        pytest.param(
            [],
            "https://example.com",
            ["/usr/bin/firefox", "-new-tab", "https://example.com"],
            id="url-only",
        ),
        pytest.param(
            [],
            None,
            ["/usr/bin/firefox"],
            id="no-args-no-url",
        ),
        pytest.param(
            ["--private-window"],
            None,
            ["/usr/bin/firefox", "--private-window"],
            id="private-window-no-url",
        ),
    ),
)
@mock.patch("subprocess.Popen")
def test_firefox_command_construction(
    mock_popen: mock.MagicMock, args: list[str], url: str | None, expected_command: list[str]
) -> None:
    browsers._launch("firefox", "/usr/bin/firefox", args, url)
    mock_popen.assert_called_once_with(expected_command)
