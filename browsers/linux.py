import configparser
import glob
import os
import re
import shlex
import shutil
import subprocess
import sys
from typing import Iterator

from .common import Browser

LINUX_DESKTOP_BROWSER_NAMES = {
    "Brave Web Browser": "brave",
    "Brave Web Browser (beta)": "brave-beta",
    "Brave Web Browser (nightly)": "brave-nightly",
    "Google Chrome": "chrome",
    "Chromium Web Browser": "chromium",
    "Falkon": "falkon",
    "Firefox": "firefox",
    "Firefox Web Browser": "firefox",
    "Konqueror": "konqueror",
    "Microsoft Edge": "msedge",
    "Opera": "opera",
    "Opera beta": "opera-beta",
    "Opera developer": "opera-developer",
    "Vivaldi": "vivaldi",
}

# $XDG_DATA_HOME and $XDG_DATA_DIRS are not always set
XDG_DATA_LOCATIONS = (
    "~/.local/share/applications",
    "/usr/share/applications",
    "/var/lib/snapd/desktop/applications",
)

VERSION_PATTERN = re.compile(r"\b(\S+\.\S+)\b")  # simple pattern assuming all version strings have a dot on them


def browsers() -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "linux":
        for application_dir in XDG_DATA_LOCATIONS:
            for desktop_file in glob.glob(os.path.join(application_dir, "*.desktop")):
                config = configparser.ConfigParser(interpolation=None)
                config.read(desktop_file, encoding="utf-8")
                if (
                    "WebBrowser" not in config.get("Desktop Entry", "Categories", fallback="").split(";")
                    and config.get("Desktop Entry", "GenericName", fallback="") != "Web Browser"
                ):
                    continue

                display_name = config.get("Desktop Entry", "Name")
                executable_path = config.get("Desktop Entry", "TryExec", fallback=config.get("Desktop Entry", "Exec"))

                # Try to remove BAMF_DESKTOP_FILE_HINT and find the actual executable/binary
                for path in shlex.split(executable_path):
                    if path == "env":
                        continue
                    if os.path.exists(path):
                        executable_path = path
                        break
                    # Find binary path from $PATH
                    # see https://specifications.freedesktop.org/desktop-entry-spec/latest/exec-variables.html
                    if result := shutil.which(path):
                        executable_path = result
                        break

                version = subprocess.getoutput(f"{executable_path} --version 2>&1").strip()
                if match := VERSION_PATTERN.search(version):
                    version = match[0]

                yield Browser(
                    browser_type=LINUX_DESKTOP_BROWSER_NAMES.get(display_name, "unknown"),
                    path=executable_path,
                    display_name=display_name,
                    version=version,
                )
