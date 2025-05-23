import configparser
import os
import re
import subprocess
import sys
from typing import Iterator

from .common import Browser

LINUX_DESKTOP_ENTRY_LIST = (
    # desktop entry name can be "firefox.desktop" or "firefox_firefox.desktop"
    ("brave", ("brave-browser", "brave_brave")),
    ("brave-beta", ("brave-browser-beta",)),
    ("brave-nightly", ("brave-browser-nightly",)),
    ("chrome", ("google-chrome",)),
    ("chromium", ("chromium", "chromium_chromium")),
    ("falkon", ("falkon_falkon",)),
    ("firefox", ("firefox", "firefox_firefox")),
    ("konqueror", ("konqueror_konqueror",)),
    ("msedge", ("microsoft-edge",)),
    ("opera", ("opera_opera",)),
    ("opera-beta", ("opera-beta_opera-beta",)),
    ("opera-developer", ("opera-developer_opera-developer",)),
    ("vivaldi", ("vivaldi_vivaldi-stable",)),
)

# $XDG_DATA_HOME and $XDG_DATA_DIRS are not always set
XDG_DATA_LOCATIONS = (
    "~/.local/share/applications",
    "/usr/share/applications",
    "/var/lib/snapd/desktop/applications",
)

VERSION_PATTERN = re.compile(r"\b(\S+\.\S+)\b")  # simple pattern assuming all version strings have a dot on them


def browsers() -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "linux":
        for browser, desktop_entries in LINUX_DESKTOP_ENTRY_LIST:
            for application_dir in XDG_DATA_LOCATIONS:
                for desktop_entry in desktop_entries:
                    path = os.path.join(application_dir, f"{desktop_entry}.desktop")

                    if not os.path.isfile(path):
                        continue

                    config = configparser.ConfigParser(interpolation=None)
                    config.read(path, encoding="utf-8")
                    executable_path = config.get("Desktop Entry", "Exec")
                    name = config.get("Desktop Entry", "Name")

                    if executable_path.lower().endswith(" %u"):
                        executable_path = executable_path[:-3].strip()

                    version = subprocess.getoutput(f"{executable_path} --version 2>&1").strip()
                    if match := VERSION_PATTERN.search(version):
                        version = match[0]

                    yield Browser(browser_type=browser, path=executable_path, display_name=name, version=version)
