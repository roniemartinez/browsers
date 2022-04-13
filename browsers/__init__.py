import logging
import os
import plistlib
import subprocess
import sys
from typing import Dict, Iterator, Optional, Sequence, Tuple

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BROWSER_LIST = (
    # browser name, bundle ID, version string
    ("chrome", "com.google.Chrome", "KSVersion"),
    ("chrome-canary", "com.google.Chrome.canary", "KSVersion"),
    ("chromium", "org.chromium.Chromium", "CFBundleShortVersionString"),
    ("firefox", "org.mozilla.firefox", "CFBundleShortVersionString"),
    ("firefox-developer", "org.mozilla.firefoxdeveloperedition", "CFBundleShortVersionString"),
    ("firefox-nightly", "org.mozilla.nightly", "CFBundleShortVersionString"),
    ("safari", "com.apple.Safari", "CFBundleShortVersionString"),
    ("opera", "com.operasoftware.Opera", "CFBundleVersion"),
    ("opera-beta", "com.operasoftware.OperaNext", "CFBundleVersion"),
    ("opera-developer", "com.operasoftware.OperaDeveloper", "CFBundleVersion"),
    ("msedge", "com.microsoft.edgemac", "CFBundleVersion"),
    ("msedge-beta", "com.microsoft.edgemac.Beta", "CFBundleVersion"),
    ("msedge-dev", "com.microsoft.edgemac.Dev", "CFBundleVersion"),
    ("msedge-canary", "com.microsoft.edgemac.Canary", "CFBundleVersion"),
    ("brave", "com.brave.Browser", "CFBundleVersion"),
    ("brave-beta", "com.brave.Browser.beta", "CFBundleVersion"),
    ("brave-dev", "com.brave.Browser.dev", "CFBundleVersion"),
    ("brave-nightly", "com.brave.Browser.nightly", "CFBundleVersion"),
)


def get_available_browsers() -> Iterator[Tuple[str, Dict]]:
    platform = sys.platform
    if platform != "darwin":  # pragma: no cover
        logger.info(
            "'%s' is currently not supported. Please open an issue or a PR at '%s'",
            platform,
            "https://github.com/roniemartinez/browsers",
        )
        return
    for browser, bundle_id, version_string in BROWSER_LIST:
        paths = subprocess.getoutput(f'mdfind "kMDItemCFBundleIdentifier == {bundle_id}"').splitlines()
        for path in paths:
            with open(os.path.join(path, "Contents/Info.plist"), "rb") as f:
                plist = plistlib.load(f)
                display_name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName", browser)
                version = plist[version_string]
                yield browser, dict(path=path, display_name=display_name, version=version)


def get(browser: str) -> Optional[Dict]:
    return dict(get_available_browsers()).get(browser)


def launch(browser: str, url: str, args: Optional[Sequence[str]] = None) -> None:
    if args is None:
        args = []
    b = get(browser)
    if not b:
        logger.info("Cannot find browser '%s'", browser)
        return
    _launch(b["path"], url, args)


def _launch(path: str, url: str, args: Sequence[str]) -> None:  # pragma: no cover
    subprocess.Popen(["open", "--wait-apps", "--new", "--fresh", "-a", path, url, "--args", *args])
