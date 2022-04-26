import fnmatch
import logging
import shlex
import subprocess
import sys
from typing import Iterator, Optional, Sequence

from . import linux, osx, windows
from .common import Browser

__all__ = ["Browser", "browsers", "get", "launch"]

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def browsers() -> Iterator[Browser]:
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


def get(browser: str, version: str = "*") -> Optional[Browser]:
    """
    Returns the information for the provided browser key.

    :param browser: Any of "chrome", "chrome-canary", "firefox", "firefox-developer", "firefox-nightly", "opera",
                    "opera-beta", "opera-developer", "msedge", "msedge-beta", "msedge-dev", "msedge-canary", "msie",
                    "brave", "brave-beta", "brave-dev", "brave-nightly", and "safari".
    :param version: Version string (supports wildcard, e.g. 100.*)
    :return: Dictionary containing "path", "display_name" and "version".
    """
    for b in browsers():
        if b["browser_type"] == browser and fnmatch.fnmatch(b["version"], version):
            return b
    return None


def launch(
    browser: str, version: str = "*", url: str = None, args: Optional[Sequence[str]] = None
) -> Optional[subprocess.Popen]:
    """
    Launches a web browser.

    :param browser: Browser key.
    :param version: Version string (supports wildcard, e.g. 100.*)
    :param url: URL.
    :param args: Arguments to be passed to the browser.
    """
    if args is None:
        args = []
    b = get(browser, version)
    if not b:
        logger.info("Cannot find browser '%s'", browser)
        return None
    return _launch(browser, b["path"], args, url)


def _launch(browser: str, path: str, args: Sequence[str], url: str = None) -> subprocess.Popen:  # pragma: no cover
    url_arg = []

    if browser == "firefox" and url is not None:
        args = ("-new-tab", url, *args)
    elif url is not None:
        url_arg.append(url)

    if browser == "safari":
        if args:
            logger.warning("Safari does not accept command line arguments. %s will be ignored.", str(args))
        command = ["open", "--wait-apps", "--new", "--fresh", "-a", path, *url_arg]
    elif sys.platform != "linux":
        command = [path, *url_arg, *args]
    else:
        command = [*shlex.split(path), *url_arg, *args]

    return subprocess.Popen(command)
