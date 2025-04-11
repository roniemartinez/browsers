import os
import plistlib
import subprocess
import sys
from typing import Iterator

from .common import Browser

OSX_BROWSER_BUNDLE_LIST = (
    # browser name, bundle ID, version string
    ("chrome", "com.google.Chrome", "CFBundleShortVersionString"),
    ("chrome-canary", "com.google.Chrome.canary", "CFBundleShortVersionString"),
    ("chromium", "org.chromium.Chromium", "CFBundleShortVersionString"),
    ("firefox", "org.mozilla.firefox", "CFBundleShortVersionString"),
    ("firefox-developer", "org.mozilla.firefoxdeveloperedition", "CFBundleShortVersionString"),
    ("firefox-nightly", "org.mozilla.nightly", "CFBundleShortVersionString"),
    ("safari", "com.apple.Safari", "CFBundleShortVersionString"),
    ("opera", "com.operasoftware.Opera", "CFBundleVersion"),
    ("opera-beta", "com.operasoftware.OperaNext", "CFBundleVersion"),
    ("opera-developer", "com.operasoftware.OperaDeveloper", "CFBundleVersion"),
    ("msedge", "com.microsoft.edgemac", "CFBundleShortVersionString"),
    ("msedge-beta", "com.microsoft.edgemac.Beta", "CFBundleShortVersionString"),
    ("msedge-dev", "com.microsoft.edgemac.Dev", "CFBundleShortVersionString"),
    ("msedge-canary", "com.microsoft.edgemac.Canary", "CFBundleShortVersionString"),
    ("brave", "com.brave.Browser", "CFBundleVersion"),
    ("brave-beta", "com.brave.Browser.beta", "CFBundleVersion"),
    ("brave-dev", "com.brave.Browser.dev", "CFBundleVersion"),
    ("brave-nightly", "com.brave.Browser.nightly", "CFBundleVersion"),
)


def browsers() -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "darwin":
        for browser, bundle_id, version_string in OSX_BROWSER_BUNDLE_LIST:
            paths = subprocess.getoutput(f'mdfind "kMDItemCFBundleIdentifier == {bundle_id}"').splitlines()
            for path in paths:
                with open(os.path.join(path, "Contents/Info.plist"), "rb") as f:
                    plist = plistlib.load(f)
                    executable_name = plist.get("CFBundleExecutable")
                    executable = os.path.join(path, "Contents/MacOS", executable_name)
                    display_name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName", browser)
                    version = plist[version_string]

                    if browser.startswith("brave"):
                        version = _reverse_brave_version(version)

                    yield Browser(
                        browser_type=browser,
                        path=executable if browser != "safari" else path,
                        display_name=display_name,
                        version=version,
                    )


def _reverse_brave_version(version: str) -> str:
    """
    Reverse the version string manipulation done by Brave
    https://github.com/brave/brave-core/blob/master/build/mac/tweak_info_plist.py#L46-L58

    >>> _reverse_brave_version("175.181")
    '1.75.181'
    >>> _reverse_brave_version("100.1.2")
    '1.0.1.2'
    """
    major_minor, patch = version.split(".", 1)
    major, minor = divmod(int(major_minor), 100)

    return f"{major}.{minor}.{patch}"
