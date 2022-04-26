import os
import plistlib
import subprocess
import sys
from typing import Iterator

from .common import Browser

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
                    yield Browser(
                        browser_type=browser,
                        path=executable if browser != "safari" else path,
                        display_name=display_name,
                        version=version,
                    )
