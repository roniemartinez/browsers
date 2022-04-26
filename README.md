<table>
    <tr>
        <td>License</td>
        <td><img src='https://img.shields.io/pypi/l/pybrowsers.svg?style=for-the-badge' alt="License"></td>
        <td>Version</td>
        <td><img src='https://img.shields.io/pypi/v/pybrowsers.svg?logo=pypi&style=for-the-badge' alt="Version"></td>
    </tr>
    <tr>
        <td>Github Actions</td>
        <td><img src='https://img.shields.io/github/workflow/status/roniemartinez/browsers/Python?label=actions&logo=github%20actions&style=for-the-badge' alt="Github Actions"></td>
        <td>Coverage</td>
        <td><img src='https://img.shields.io/codecov/c/github/roniemartinez/browsers/branch?label=codecov&logo=codecov&style=for-the-badge' alt="CodeCov"></td>
    </tr>
    <tr>
        <td>Supported versions</td>
        <td><img src='https://img.shields.io/pypi/pyversions/pybrowsers.svg?logo=python&style=for-the-badge' alt="Python Versions"></td>
        <td>Wheel</td>
        <td><img src='https://img.shields.io/pypi/wheel/pybrowsers.svg?style=for-the-badge' alt="Wheel"></td>
    </tr>
    <tr>
        <td>Status</td>
        <td><img src='https://img.shields.io/pypi/status/pybrowsers.svg?style=for-the-badge' alt="Status"></td>
        <td>Downloads</td>
        <td><img src='https://img.shields.io/pypi/dm/pybrowsers.svg?style=for-the-badge' alt="Downloads"></td>
    </tr>
</table>

# browsers

Python library for detecting and launching browsers


## Why?

I recently wrote a snippet for detecting installed browsers in an OSX machine in 
https://github.com/mitmproxy/mitmproxy/issues/5247#issuecomment-1095337723 based on https://github.com/httptoolkit/browser-launcher
and I thought this could be useful to other devs since I cannot find an equivalent library of `httptoolkit/browser-launcher` in Python
and the known `webbrowser` standard library does not support arguments.

## Installation

```bash
pip install pybrowsers
```

## Features

- Detect browser on OSX
- Detect browser on Linux
- Detect browser on Windows
- Launch browser with arguments
- Launch and get browser by version with wildcard support

## Usage

### Import

```python
import browsers
```

### List all installer browsers

```python
import browsers

print(list(browsers.browsers()))
# [{'browser_type': 'chrome', 'path': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'display_name': 'Google Chrome', 'version': '100.0.4896.127'}, {'browser_type': 'firefox', 'path': '/Applications/Firefox.app/Contents/MacOS/firefox', 'display_name': 'Firefox', 'version': '99.0.1'}, {'browser_type': 'safari', 'path': '/Applications/Safari.app/Contents/MacOS/Safari', 'display_name': 'Safari', 'version': '15.4'}, {'browser_type': 'opera', 'path': '/Applications/Opera.app/Contents/MacOS/Opera', 'display_name': 'Opera', 'version': '85.0.4341.60'}, {'browser_type': 'msedge', 'path': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', 'display_name': 'Microsoft Edge', 'version': '100.1185.22042050'}]
```

### Get browser information

```python
import browsers

print(browsers.get("chrome"))
# {'browser_type': 'chrome', 'path': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'display_name': 'Google Chrome', 'version': '100.0.4896.127'}
```

### Launch browser

```python
import browsers

browsers.launch("chrome")
```

### Launch browser with URL

```python
import browsers

browsers.launch("chrome", url="https://github.com/roniemartinez/browsers")
```

### Launch browser with arguments

```python
import browsers

browsers.launch("chrome", args=["--incognito"])
```

### Specifying version

The `get()` and `launch()` functions support specifying version in case multiple versions are installed.
Wildcard pattern is also supported.

```python
import browsers

print(browsers.get("chrome", version="100.0.4896.127"))  # complete version
# {'browser_type': 'chrome', 'path': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'display_name': 'Google Chrome', 'version': '100.0.4896.127'}

print(browsers.get("chrome", version="100.*"))  # wildcard
# {'browser_type': 'chrome', 'path': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'display_name': 'Google Chrome', 'version': '100.0.4896.127'}

browsers.launch("chrome", version="100.0.4896.127")  # complete version
browsers.launch("chrome", version="100.*")  # wildcard
```

## References

- [httptoolkit/browser-launcher](https://github.com/httptoolkit/browser-launcher)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [Github: webbrowser.open incomplete on Windows](https://github.com/python/cpython/issues/52479#issuecomment-1093496412)
- [Stackoverflow: Grabbing full file version of an exe in Python](https://stackoverflow.com/a/68774871/1279157)

## Author

- [Ronie Martinez](mailto:ronmarti18@gmail.com)
