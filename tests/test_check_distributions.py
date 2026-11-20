"""Tests for the METADATA version reader in tools/check_distributions.py.

The CI and release workflows use that tool to check that the built distributions carry the
expected version. Skipped when the test suite runs against an installed distribution from a copy
of tests/ (UNCERTAINTYLIB_TEST_INSTALLED=1), where tools/ is not available.
"""

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("UNCERTAINTYLIB_TEST_INSTALLED") == "1",
                                reason="checks a repository tool, not the installed package")

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def check_distributions():
    spec = importlib.util.spec_from_file_location(
        "check_distributions", REPOSITORY_ROOT / "tools" / "check_distributions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_metadata_version_with_lf_and_crlf(check_distributions, newline):
    text = newline.join(["Metadata-Version: 2.4", "Name: uncertaintylib", "Version: 1.2.0",
                         "Summary: x", "", "Version: 9.9.9 in the description", ""])
    assert check_distributions._metadata_version(text) == "1.2.0"


def test_metadata_version_reads_only_the_header_block(check_distributions):
    text = "Metadata-Version: 2.4\nName: uncertaintylib\n\nVersion: 1.2.0\n"
    assert check_distributions._metadata_version(text) is None


def test_metadata_version_does_not_match_metadata_version_field(check_distributions):
    assert check_distributions._metadata_version("Metadata-Version: 2.4\n") is None
