import os
import subprocess
import sys
from typing import Dict, Iterator, Tuple

LINUX_DESKTOP_ENTRY_LIST = (
    # desktop entry name can be "firefox.desktop" or "firefox_firefox.desktop"
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


def browsers() -> Iterator[Tuple[str, Dict]]:  # type: ignore[return]
    if sys.platform == "linux":
        from xdg.DesktopEntry import DesktopEntry

        for browser, desktop_entries in LINUX_DESKTOP_ENTRY_LIST:
            for application_dir in XDG_DATA_LOCATIONS:
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
