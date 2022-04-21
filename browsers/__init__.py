import logging
import shlex
import subprocess
import sys
from typing import Dict, Iterator, Optional, Sequence, Tuple

from . import linux, osx, windows

__all__ = ["browsers", "get", "launch"]

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def browsers() -> Iterator[Tuple[str, Dict]]:
    """
    Iterates over installed browsers.

    :return: Iterator of Tuple of browser key and browser information.
    """
    if sys.platform == "linux":
        yield from linux.browsers()
    elif sys.platform == "win32":
        yield from windows.browsers()
    elif sys.platform == "darwin":
        yield from osx.browsers()
    else:  # pragma: no cover
        logger.info(
            "'%s' is currently not supported. Please open an issue or a PR at '%s'",
            sys.platform,
            "https://github.com/roniemartinez/browsers",
        )


def get(browser: str) -> Optional[Dict]:
    """
    Returns the information for the provided browser key.

    :param browser: Any of "chrome", "chrome-canary", "firefox", "firefox-developer", "firefox-nightly", "opera",
                    "opera-beta", "opera-developer", "msedge", "msedge-beta", "msedge-dev", "msedge-canary", "msie",
                    "brave", "brave-beta", "brave-dev", "brave-nightly", and "safari".
    :return: Dictionary containing "path", "display_name" and "version".
    """
    for key, value in browsers():
        if key == browser:
            return value
    return None


def launch(browser: str, url: str = None, args: Optional[Sequence[str]] = None) -> None:
    """
    Launches a web browser.

    :param browser: Browser key.
    :param url: URL.
    :param args: Arguments to be passed to the browser.
    """
    if args is None:
        args = []
    b = get(browser)
    if not b:
        logger.info("Cannot find browser '%s'", browser)
        return
    _launch(browser, b["path"], args, url)


def _launch(browser: str, path: str, args: Sequence[str], url: str = None) -> None:  # pragma: no cover
    url_arg = []

    if browser == "firefox" and url is not None:
        args = ("-new-tab", url, *args)
    elif url is not None:
        url_arg.append(url)

    if sys.platform != "linux":
        command = [path, *url_arg, "--args", *args]
    else:
        command = [*shlex.split(path), *url_arg, "--args", *args]

    if sys.platform == "darwin":
        command = ["open", "--wait-apps", "--new", "--fresh", "-a", *command]

    subprocess.Popen(command)
