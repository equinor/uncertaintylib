"""Check, inside the pytest run, that the package under test is the installed distribution.

The CI workflows install the built wheel and the sdist into clean virtual environments and run a
copy of this test suite against them. That only proves something if the tests import the
installed package and not the source tree in the checkout. This test checks that from within the
same pytest session that runs the other tests, so a change in how pytest sets up ``sys.path``
cannot make the distribution test silently test the checkout instead.

It is active only when the environment variable ``UNCERTAINTYLIB_TEST_INSTALLED`` is ``1``, which
the workflows set. In a normal local run the package is usually an editable install from the
source tree, so the test is skipped there.

Environment variables read by the test:

- ``GITHUB_WORKSPACE``: the checkout. The package must not be imported from inside it.
- ``UNCERTAINTYLIB_EXPECTED_VERSION`` (optional): the version the distribution must report, which
  is the version in the file names of the built distributions.
"""

import importlib.metadata
import os
import sys

import pytest

import uncertaintylib


def _is_inside(path, folder):
    path = os.path.normcase(os.path.realpath(path))
    folder = os.path.normcase(os.path.realpath(folder))
    return os.path.commonpath([path, folder]) == folder


@pytest.mark.skipif(os.environ.get("UNCERTAINTYLIB_TEST_INSTALLED") != "1",
                    reason="only checked when testing an installed distribution "
                           "(UNCERTAINTYLIB_TEST_INSTALLED=1)")
def test_package_is_imported_from_the_installed_distribution():
    location = uncertaintylib.__file__
    print("uncertaintylib imported from", location)
    print("uncertaintylib.__version__", uncertaintylib.__version__)

    workspace = os.environ.get("GITHUB_WORKSPACE")
    assert workspace, "GITHUB_WORKSPACE must be set to the checkout when this test is active"
    assert not _is_inside(location, workspace), (
        f"uncertaintylib was imported from {location}, inside the checkout {workspace}, "
        "not from the installed distribution"
    )
    assert _is_inside(location, sys.prefix), (
        f"uncertaintylib was imported from {location}, outside the environment {sys.prefix}"
    )

    expected_version = os.environ.get("UNCERTAINTYLIB_EXPECTED_VERSION")
    if expected_version:
        assert uncertaintylib.__version__ == expected_version
        assert importlib.metadata.version("uncertaintylib") == expected_version
