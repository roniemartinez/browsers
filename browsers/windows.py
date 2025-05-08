import contextlib
import ctypes
import os
import sys
from ctypes import wintypes
from typing import Iterator

from .common import Browser

WINDOWS_REGISTRY_BROWSER_NAMES = {
    "Ablaze Floorp": "floorp",
    "Basilisk": "basilisk",
    "Brave": "brave",
    "Brave Beta": "brave-beta",
    "Brave Nightly": "brave-nightly",
    "Chromium": "chromium",
    "Firefox Developer Edition": "firefox-developer",
    "Firefox Nightly": "firefox-nightly",
    "Google Chrome": "chrome",
    "Google Chrome Canary": "chrome-canary",
    "Internet Explorer": "msie",
    "LibreWolf": "librewolf",
    "Microsoft Edge": "msedge",
    "Microsoft Edge Beta": "msedge-beta",
    "Microsoft Edge Dev": "msedge-dev",
    "Microsoft Edge Canary": "msedge-canary",
    "Mozilla Firefox": "firefox",
    "Opera Stable": "opera",
    "Opera beta": "opera-beta",
    "Opera developer": "opera-developer",
    "Pale Moon": "pale-moon",
    "Waterfox": "waterfox",
}


def browsers() -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "win32":
        import winreg

        yield from _win32_browsers_from_registry(winreg.HKEY_CURRENT_USER, winreg.KEY_READ)
        yield from _win32_browsers_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        yield from _win32_browsers_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)


def _win32_browsers_from_registry(tree: int, access: int) -> Iterator[Browser]:  # type: ignore[return]
    if sys.platform == "win32":
        import winreg

        with contextlib.suppress(FileNotFoundError):
            with winreg.OpenKey(tree, r"Software\Clients\StartMenuInternet", access=access) as hkey:
                i = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(hkey, i)
                        i += 1
                    except OSError:
                        break

                    try:
                        display_name = winreg.QueryValue(hkey, subkey)
                        if not display_name or not isinstance(display_name, str):  # pragma: no cover
                            display_name = subkey
                    except OSError:  # pragma: no cover
                        display_name = subkey

                    try:
                        cmd = winreg.QueryValue(hkey, rf"{subkey}\shell\open\command")
                        cmd = cmd.strip('"')
                        os.stat(cmd)
                    except (OSError, AttributeError, TypeError, ValueError):  # pragma: no cover
                        continue

                    yield Browser(
                        browser_type=WINDOWS_REGISTRY_BROWSER_NAMES.get(display_name, "unknown"),
                        path=cmd,
                        display_name=display_name,
                        version=_get_file_version(cmd),
                    )


class VS_FIXEDFILEINFO(ctypes.Structure):
    _fields_ = [
        ("dwSignature", wintypes.DWORD),
        ("dwStrucVersion", wintypes.DWORD),
        ("dwFileVersionMS", wintypes.DWORD),
        ("dwFileVersionLS", wintypes.DWORD),
        ("dwProductVersionMS", wintypes.DWORD),
        ("dwProductVersionLS", wintypes.DWORD),
        ("dwFileFlagsMask", wintypes.DWORD),
        ("dwFileFlags", wintypes.DWORD),
        ("dwFileOS", wintypes.DWORD),
        ("dwFileType", wintypes.DWORD),
        ("dwFileSubtype", wintypes.DWORD),
        ("dwFileDateMS", wintypes.DWORD),
        ("dwFileDateLS", wintypes.DWORD),
    ]


def _get_file_version(file_path: str) -> str:
    if sys.platform == "win32":
        if not (size := ctypes.windll.version.GetFileVersionInfoSizeW(file_path, None)):
            return ""

        buffer = ctypes.create_string_buffer(size)

        if not ctypes.windll.version.GetFileVersionInfoW(file_path, 0, size, buffer):
            return ""

        lplp_buffer = ctypes.c_void_p()
        u_len = wintypes.UINT()
        ctypes.windll.version.VerQueryValueW(buffer, "\\", ctypes.byref(lplp_buffer), ctypes.byref(u_len))

        if not lplp_buffer.value:
            return ""

        ffi = ctypes.cast(lplp_buffer.value, ctypes.POINTER(VS_FIXEDFILEINFO)).contents

        dw_file_version_ms = ffi.dwFileVersionMS
        dw_file_version_ls = ffi.dwFileVersionLS

        major = (dw_file_version_ms >> 16) & 0xFFFF
        minor = dw_file_version_ms & 0xFFFF
        build = (dw_file_version_ls >> 16) & 0xFFFF
        revision = dw_file_version_ls & 0xFFFF

        return f"{major}.{minor}.{build}.{revision}"

    return ""
