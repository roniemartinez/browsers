from typing import Dict
from unittest import mock
from unittest.mock import ANY

import pytest

import browsers
from browsers import get_available_browsers

"""
These tests assume that Chrome, Firefox, Safari and Microsoft Edge are installed. These are available in Github Actions.
"""


def test_get_available_browsers() -> None:
    available_browsers = dict(get_available_browsers())
    assert "chrome" in available_browsers
    assert "firefox" in available_browsers
    assert "safari" in available_browsers
    assert "msedge" in available_browsers


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
            id="chrome",
        ),
        pytest.param(
            "firefox",
            {
                "display_name": "Firefox",
                "path": "/Applications/Firefox.app",
                "version": ANY,
            },
            id="firefox",
        ),
        pytest.param(
            "safari",
            {
                "display_name": "Safari",
                "path": "/Applications/Safari.app",
                "version": ANY,
            },
            id="safari",
        ),
        pytest.param(
            "msedge",
            {
                "display_name": "Microsoft Edge",
                "path": "/Applications/Microsoft Edge.app",
                "version": ANY,
            },
            id="msedge",
        ),
    ),
)
def test_get(browser: str, details: Dict) -> None:
    assert browsers.get(browser) == details


@mock.patch.object(browsers, "_launch")
def test_launch(mock_launch: mock.MagicMock) -> None:
    browsers.launch("chrome", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_called_with("/Applications/Google Chrome.app", "https://github.com/roniemartinez/browsers", [])


@mock.patch.object(browsers, "_launch")
def test_launch_no_browser(mock_launch: mock.MagicMock) -> None:
    browsers.launch("hello", url="https://github.com/roniemartinez/browsers")
    mock_launch.assert_not_called()
