import glob
import os
import plistlib
import subprocess
import sys
from typing import Iterator

from .common import Browser

OSX_BROWSER_BUNDLE_LIST = (
    # browser name, bundle ID, version string
    ("basilisk", "org.mozilla.basilisk", "CFBundleShortVersionString"),
    ("brave", "com.brave.Browser", "CFBundleVersion"),
    ("brave-beta", "com.brave.Browser.beta", "CFBundleVersion"),
    ("brave-dev", "com.brave.Browser.dev", "CFBundleVersion"),
    ("brave-nightly", "com.brave.Browser.nightly", "CFBundleVersion"),
    ("chrome", "com.google.Chrome", "CFBundleShortVersionString"),
    ("chrome-beta", "com.google.Chrome.beta", "CFBundleShortVersionString"),
    ("chrome-canary", "com.google.Chrome.canary", "CFBundleShortVersionString"),
    ("chrome-dev", "com.google.Chrome.dev", "CFBundleShortVersionString"),
    ("chrome-test", "com.google.chrome.for.testing", "CFBundleShortVersionString"),
    ("chromium", "org.chromium.Chromium", "CFBundleShortVersionString"),
    ("duckduckgo", "com.duckduckgo.macos.browser", "CFBundleShortVersionString"),
    ("epic", "com.hiddenreflex.Epic", "CFBundleShortVersionString"),
    ("firefox", "org.mozilla.firefox", "CFBundleShortVersionString"),
    ("firefox-developer", "org.mozilla.firefoxdeveloperedition", "CFBundleShortVersionString"),
    ("firefox-nightly", "org.mozilla.nightly", "CFBundleShortVersionString"),
    ("floorp", "org.mozilla.floorp", "CFBundleShortVersionString"),
    ("librewolf", "org.mozilla.librewolf", "CFBundleShortVersionString"),
    ("midori", "org.mozilla.midori", "CFBundleShortVersionString"),
    ("msedge", "com.microsoft.edgemac", "CFBundleShortVersionString"),
    ("msedge-beta", "com.microsoft.edgemac.Beta", "CFBundleShortVersionString"),
    ("msedge-dev", "com.microsoft.edgemac.Dev", "CFBundleShortVersionString"),
    ("msedge-canary", "com.microsoft.edgemac.Canary", "CFBundleShortVersionString"),
    ("opera", "com.operasoftware.Opera", "CFBundleVersion"),
    ("opera-beta", "com.operasoftware.OperaNext", "CFBundleVersion"),
    ("opera-developer", "com.operasoftware.OperaDeveloper", "CFBundleVersion"),
    ("opera-gx", "com.operasoftware.OperaGX", "CFBundleVersion"),
    ("opera-neon", "com.opera.Neon", "CFBundleShortVersionString"),
    ("pale-moon", "org.mozilla.pale moon", "CFBundleShortVersionString"),
    ("safari", "com.apple.Safari", "CFBundleShortVersionString"),
    ("safari-technology-preview", "com.apple.SafariTechnologyPreview", "CFBundleShortVersionString"),
    ("servo", "org.servo.Servo", "CFBundleShortVersionString"),
    ("vivaldi", "com.vivaldi.Vivaldi", "CFBundleShortVersionString"),
    ("waterfox", "net.waterfox.waterfox", "CFBundleShortVersionString"),
    ("yandex", "ru.yandex.desktop.yandex-browser", "CFBundleShortVersionString"),
    ("zen", "app.zen-browser.zen", "CFBundleShortVersionString"),
)

OSX_BROWSER_BUNDLE_DICT = {item[1]: item for item in OSX_BROWSER_BUNDLE_LIST}


def browsers() -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "darwin":
        found_browser_plists = set()

        for browser, bundle_id, version_string in OSX_BROWSER_BUNDLE_LIST:
            app_dirs = subprocess.getoutput(f'mdfind "kMDItemCFBundleIdentifier == {bundle_id}"').splitlines()
            for app_dir in app_dirs:
                plist_path = os.path.join(app_dir, "Contents/Info.plist")
                if plist_path in found_browser_plists:
                    continue

                found_browser_plists.add(plist_path)

                with open(plist_path, "rb") as f:
                    plist = plistlib.load(f)
                    yield _get_browser_info(app_dir, browser, plist, version_string)

        # Naively iterate /Applications folder in case the above check fails
        for plist_path in glob.glob("/Applications/*.app/Contents/Info.plist"):
            if plist_path in found_browser_plists:
                continue

            with open(plist_path, "rb") as f:
                plist = plistlib.load(f)
                bundle_id = plist.get("CFBundleIdentifier")
                if bundle_id not in OSX_BROWSER_BUNDLE_DICT:
                    continue

                found_browser_plists.add(plist_path)
                browser, _, version_string = OSX_BROWSER_BUNDLE_DICT[bundle_id]
                app_dir = os.path.dirname(os.path.dirname(plist_path))

                yield _get_browser_info(app_dir, browser, plist, version_string)


def _get_browser_info(app_dir: str, browser: str, plist: dict, version_string: str) -> Browser:
    executable_name = plist["CFBundleExecutable"]
    executable = os.path.join(app_dir, "Contents/MacOS", executable_name)
    display_name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName", browser)
    version = plist[version_string]

    if browser.startswith("brave"):  # pragma: no cover
        version = _reverse_brave_version(version)

    return Browser(
        browser_type=browser,
        path=executable if browser != "safari" else app_dir,
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
