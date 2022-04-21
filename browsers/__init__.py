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
    ("chromium", ("chromium", "chromium_chromium")),
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

WINDOWS_REGISTRY_BROWSER_NAMES = {
    "Google Chrome": "chrome",
    "Google Chrome Canary": "chrome-canary",
    "Mozilla Firefox": "firefox",
    "Firefox Developer Edition": "firefox-developer",
    "Firefox Nightly": "firefox-nightly",
    "Opera Stable": "opera",
    "Opera beta": "opera-beta",
    "Opera developer": "opera-developer",
    "Microsoft Edge": "msedge",
    "Microsoft Edge Beta": "msedge-beta",
    "Microsoft Edge Dev": "msedge-dev",
    "Microsoft Edge Canary": "msedge-canary",
    "Internet Explorer": "msie",
    "Brave": "brave",
    "Brave Beta": "brave-beta",
    "Brave Nightly": "brave-nightly",
}


def get_available_browsers() -> Iterator[Tuple[str, Dict]]:
    if sys.platform == "linux":
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
    elif sys.platform == "win32":
        import winreg

        yield from get_browsers_from_registry(winreg.HKEY_CURRENT_USER, winreg.KEY_READ)
        yield from get_browsers_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        yield from get_browsers_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
    elif sys.platform == "darwin":
        for browser, bundle_id, version_string in OSX_BROWSER_BUNDLE_LIST:
            paths = subprocess.getoutput(f'mdfind "kMDItemCFBundleIdentifier == {bundle_id}"').splitlines()
            for path in paths:
                with open(os.path.join(path, "Contents/Info.plist"), "rb") as f:
                    plist = plistlib.load(f)
                    display_name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName", browser)
                    version = plist[version_string]
                    yield browser, dict(path=path, display_name=display_name, version=version)
    else:  # pragma: no cover
        logger.info(
            "'%s' is currently not supported. Please open an issue or a PR at '%s'",
            sys.platform,
            "https://github.com/roniemartinez/browsers",
        )


def get_browsers_from_registry(tree: int, access: int) -> Iterator[Tuple[str, Dict]]:  # type: ignore[return]
    if sys.platform == "win32":
        import winreg

        key = r"Software\Clients\StartMenuInternet"
        try:
            with winreg.OpenKey(tree, key, access=access) as hkey:
                i = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(hkey, i)
                        i += 1
                    except OSError:
                        break
                    try:
                        name = winreg.QueryValue(hkey, subkey)
                        if not name or not isinstance(name, str):
                            name = subkey
                    except OSError:
                        name = subkey
                    try:
                        cmd = winreg.QueryValue(hkey, rf"{subkey}\shell\open\command")
                        cmd = cmd.strip('"')
                        os.stat(cmd)
                    except (OSError, AttributeError, TypeError, ValueError):
                        continue
                    info = dict(path=cmd, display_name=name, version=get_file_version(cmd))
                    yield WINDOWS_REGISTRY_BROWSER_NAMES.get(name, "unknown"), info
        except FileNotFoundError:
            pass


def get_file_version(path: str) -> Optional[str]:
    if sys.platform == "win32":
        import win32api

        info = win32api.GetFileVersionInfo(path, "\\")
        ms = info["FileVersionMS"]
        ls = info["FileVersionLS"]
        return ".".join(map(str, (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))))
    return None


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
    _launch(browser, b["path"], url, args)


def _launch(browser: str, path: str, url: str, args: Sequence[str]) -> None:  # pragma: no cover
    url_arg = [] if browser == "firefox" else [url]
    if browser == "firefox":
        args = ("-new-tab", url, *args)
    if sys.platform == "win32":
        command = [path, *url_arg, "--args", *args]
    else:
        command = [*shlex.split(path), *url_arg, "--args", *args]
    if sys.platform == "darwin":
        command = ["open", "--wait-apps", "--new", "--fresh", "-a", *command]
    subprocess.Popen(command)
