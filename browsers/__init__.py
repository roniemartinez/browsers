import logging
import os
import plistlib
import shlex
import subprocess
import sys
from typing import Dict, Iterator, Optional, Sequence, Tuple

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OSX_BROWSER_BUNDLE_LIST = (
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

LINUX_DESKTOP_ENTRY_LIST = (
    ("chrome", ("google-chrome",)),
    ("chromium", ("chromium",)),
    ("firefox", ("firefox", "firefox_firefox")),
    ("msedge", ("microsoft-edge",)),
    ("opera", ("opera_opera",)),
    ("opera-beta", ("opera-beta_opera-beta",)),
    ("opera-developer", ("opera-developer_opera-developer",)),
    ("brave", ("brave-browser", "brave_brave")),
    ("brave-beta", ("brave-browser-beta",)),
    ("brave-nightly", ("brave-browser-nightly",)),
)

# $XDG_DATA_HOME and $XDG_DATA_DIRS are not always set
XDG_DATA_LOCATIONS = (
    "~/.local/share/applications",
    "/usr/share/applications",
    "/var/lib/snapd/desktop/applications",
)


def get_available_browsers() -> Iterator[Tuple[str, Dict]]:
    platform = sys.platform
    if platform == "linux":
        from xdg.DesktopEntry import DesktopEntry

        for browser, desktop_entries in LINUX_DESKTOP_ENTRY_LIST:
            for application_dir in XDG_DATA_LOCATIONS:
                # desktop entry name can be "firefox.desktop" or "firefox_firefox.desktop"
                for desktop_entry in desktop_entries:
                    path = os.path.join(application_dir, f"{desktop_entry}.desktop")
                    if not os.path.isfile(path):
                        continue
                    entry = DesktopEntry(path)
                    executable_path = entry.getExec()
                    if executable_path.lower().endswith(" %u"):
                        executable_path = executable_path[:-3].strip()
                    # FIXME: --version includes the name for most browsers
                    version = subprocess.getoutput(f"{executable_path} --version")
                    info = dict(path=executable_path, display_name=entry.getName(), version=version)
                    yield browser, info
        return
    if platform != "darwin":  # pragma: no cover
        logger.info(
            "'%s' is currently not supported. Please open an issue or a PR at '%s'",
            platform,
            "https://github.com/roniemartinez/browsers",
        )
        return
    for browser, bundle_id, version_string in OSX_BROWSER_BUNDLE_LIST:
        paths = subprocess.getoutput(f'mdfind "kMDItemCFBundleIdentifier == {bundle_id}"').splitlines()
        for path in paths:
            with open(os.path.join(path, "Contents/Info.plist"), "rb") as f:
                plist = plistlib.load(f)
                display_name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName", browser)
                version = plist[version_string]
                yield browser, dict(path=path, display_name=display_name, version=version)


def get(browser: str) -> Optional[Dict]:
    for key, value in get_available_browsers():
        if key == browser:
            return value
    return None


def launch(browser: str, url: str, args: Optional[Sequence[str]] = None) -> None:
    if args is None:
        args = []
    b = get(browser)
    if not b:
        logger.info("Cannot find browser '%s'", browser)
        return
    _launch(b["path"], url, args)


def _launch(path: str, url: str, args: Sequence[str]) -> None:  # pragma: no cover
    command = [*shlex.split(path), url, "--args", *args]
    if sys.platform == "darwin":
        command = ["open", "--wait-apps", "--new", "--fresh", "-a", *command]
    subprocess.Popen(command)
