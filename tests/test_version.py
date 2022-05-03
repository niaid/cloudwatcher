# verify that the version is correct
from cloudwatcher._version import __version__


def test_version():
    assert __version__ == "0.0.6"
