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

> I recently wrote a snippet for detecting installed browsers in an OSX machine in 
> https://github.com/mitmproxy/mitmproxy/issues/5247#issuecomment-1095337723 based on https://github.com/httptoolkit/browser-launcher
> and I thought this could be useful to other devs since I cannot seem to find an equivalent library in Python

## Installation

```bash
pip install pybrowsers
```

## Usage

### Python

```python
>>> import browsers
>>> browsers.get("chrome")
{'path': '/Applications/Google Chrome.app', 'display_name': 'Google Chrome', 'version': '100.0.4896.88'}
>>> browsers.launch("chrome", url="https://github.com/roniemartinez/browsers")
```

## TODO:

- [x] Detect browser on OSX
- [x] Detect browser on Linux
- [X] Detect browser on Windows
- [x] Launch browser with arguments
- [ ] Get browser by version (support wildcards)

## References

- [httptoolkit/browser-launcher](https://github.com/httptoolkit/browser-launcher)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [Github: webbrowser.open incomplete on Windows](https://github.com/python/cpython/issues/52479#issuecomment-1093496412)
- [Stackoverflow: Grabbing full file version of an exe in Python](https://stackoverflow.com/a/68774871/1279157)

## Author

- [Ronie Martinez](mailto:ronmarti18@gmail.com)
