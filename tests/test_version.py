"""Tests for the package version, uncertaintylib.__version__.

The version is set in pyproject.toml and read back from the metadata of the installed
distribution. These tests check that the version the code reports is the version pip installed it
as, so a calculation can be traced to a release.
"""

import importlib.metadata

import uncertaintylib


def test_version_matches_installed_package_metadata():
    # Fails if the code being tested is not the code that was installed. The fix is to reinstall:
    # pip install -e .
    installed = importlib.metadata.version("uncertaintylib")
    assert uncertaintylib.__version__ == installed


def test_version_is_not_the_unknown_fallback():
    assert uncertaintylib.__version__ != "0+unknown"
