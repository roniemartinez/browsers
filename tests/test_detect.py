from browsers import get_available_browsers

"""
These tests assume that there are installed browsers.
"""


def test_get_available_browsers() -> None:
    browsers = dict(get_available_browsers())
    print(browsers)
    assert len(browsers)
    assert False
