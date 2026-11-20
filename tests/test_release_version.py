"""Tests for tools/release_version.py, which works out the next release version from the git tags.

The release workflow relies on this to name the release, so a wrong answer would publish a release
under the wrong version. Tag lists are given explicitly in each test.

These tests check a tool in the repository, not the package. They are skipped when the test suite
runs against an installed distribution from a copy of tests/ (UNCERTAINTYLIB_TEST_INSTALLED=1),
where tools/ is not available.
"""

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("UNCERTAINTYLIB_TEST_INSTALLED") == "1",
                                reason="checks a repository tool, not the installed package")

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# The release tags of uncertaintylib on GitHub when the release workflow was introduced
# (git tag --list). They have no prefix.
REPOSITORY_TAGS = ["0.1.0", "0.2.0", "1.0.0", "1.0.1", "1.1.0", "1.1.1", "1.1.2"]


def _load_release_version():
    spec = importlib.util.spec_from_file_location(
        "release_version", REPOSITORY_ROOT / "tools" / "release_version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def release_version():
    return _load_release_version()


class _Stdin:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text


# --- The real tags of this repository ------------------------------------------------------------

def test_latest_release_of_the_repository_tags(release_version):
    assert release_version.latest_release(REPOSITORY_TAGS) == (1, 1, 2)


def test_next_version_from_the_repository_tags(release_version):
    latest = release_version.latest_release(REPOSITORY_TAGS)
    assert release_version.next_version(latest, "patch") == (1, 1, 3)
    assert release_version.next_version(latest, "minor") == (1, 2, 0)
    assert release_version.next_version(latest, "major") == (2, 0, 0)


def test_main_with_the_repository_tags(release_version, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _Stdin("\n".join(REPOSITORY_TAGS) + "\n"))
    assert release_version.main(["--bump", "patch"]) == 0
    assert capsys.readouterr().out == "1.1.3\n"
    monkeypatch.setattr("sys.stdin", _Stdin("\n".join(REPOSITORY_TAGS) + "\n"))
    assert release_version.main(["--bump", "minor"]) == 0
    assert capsys.readouterr().out == "1.2.0\n"


# --- parse_release_tag ---------------------------------------------------------------------------

def test_parse_release_tag_without_prefix(release_version):
    assert release_version.parse_release_tag("1.1.2") == (1, 1, 2)
    assert release_version.parse_release_tag("0.1.0") == (0, 1, 0)
    assert release_version.parse_release_tag("0.0.0") == (0, 0, 0)
    assert release_version.parse_release_tag("10.20.300") == (10, 20, 300)


def test_parse_release_tag_with_prefix(release_version):
    assert release_version.parse_release_tag("v1.1.2", "v") == (1, 1, 2)
    with pytest.raises(ValueError):
        release_version.parse_release_tag("1.1.2", "v")


@pytest.mark.parametrize("tag", [
    "v1.2.5",         # prefix, but this repository has none
    "1.2",            # missing patch
    "1.2.5.1",        # four parts
    "1.2.5rc1",       # pre-release
    "1.2.5-beta",     # pre-release
    "1.2.5.post1",    # post-release
    "01.2.5",         # leading zero
    "1.02.5",         # leading zero
    "1.2.-5",         # negative
    "1.2.5 ",         # trailing space
    "",
])
def test_parse_release_tag_rejects_anything_but_major_minor_patch(release_version, tag):
    with pytest.raises(ValueError):
        release_version.parse_release_tag(tag)


# --- latest_release ------------------------------------------------------------------------------

def test_latest_release_with_no_tags_is_zero(release_version):
    assert release_version.latest_release([]) == (0, 0, 0)
    assert release_version.latest_release(["", "   "]) == (0, 0, 0)


def test_latest_release_compares_numerically_not_as_text(release_version):
    assert release_version.latest_release(["1.9.0", "1.10.0", "1.2.0"]) == (1, 10, 0)
    assert release_version.latest_release(["0.1.9", "0.1.10"]) == (0, 1, 10)
    assert release_version.latest_release(["9.0.0", "10.0.0"]) == (10, 0, 0)


def test_latest_release_does_not_depend_on_order(release_version):
    assert release_version.latest_release(REPOSITORY_TAGS) == (1, 1, 2)
    assert release_version.latest_release(list(reversed(REPOSITORY_TAGS))) == (1, 1, 2)


def test_latest_release_strips_whitespace_and_line_endings(release_version):
    assert release_version.latest_release(["0.1.0\r", "  0.2.0  ", ""]) == (0, 2, 0)


def test_latest_release_ignores_tags_that_do_not_start_with_a_digit(release_version):
    tags = ["0.3.0", "docs-preview", "v5.0.0", "validation-2026", "very-old"]
    assert release_version.latest_release(tags) == (0, 3, 0)


def test_latest_release_with_prefix_ignores_unprefixed_tags(release_version):
    assert release_version.latest_release(["v0.3.0", "5.0.0", "docs"], "v") == (0, 3, 0)


@pytest.mark.parametrize("bad_tag", ["2.0", "2.0.0rc1", "02.0.0", "2.0.0-beta", "2.0.0.1"])
def test_latest_release_rejects_malformed_digit_leading_tag(release_version, bad_tag):
    # Skipping "2.0" would make the next release 1.1.3, i.e. go backwards.
    with pytest.raises(ValueError):
        release_version.latest_release([*REPOSITORY_TAGS, bad_tag])


# --- next_version --------------------------------------------------------------------------------

def test_next_version_without_any_release(release_version):
    assert release_version.next_version((0, 0, 0), "patch") == (0, 0, 1)
    assert release_version.next_version((0, 0, 0), "minor") == (0, 1, 0)
    assert release_version.next_version((0, 0, 0), "major") == (1, 0, 0)


def test_next_version_carries_past_nine(release_version):
    assert release_version.next_version((0, 9, 9), "patch") == (0, 9, 10)
    assert release_version.next_version((0, 9, 9), "minor") == (0, 10, 0)
    assert release_version.next_version((9, 9, 9), "major") == (10, 0, 0)


@pytest.mark.parametrize("bump", ["", "Patch", "MINOR", "build", "pre"])
def test_next_version_rejects_unknown_bump(release_version, bump):
    with pytest.raises(ValueError):
        release_version.next_version((1, 1, 2), bump)


# --- format_version ------------------------------------------------------------------------------

def test_format_version(release_version):
    assert release_version.format_version((1, 1, 2)) == "1.1.2"
    assert release_version.format_version((0, 1, 0)) == "0.1.0"
    assert release_version.format_version((10, 0, 12)) == "10.0.12"


def test_format_version_round_trips_through_tag(release_version):
    for version in [(0, 0, 1), (0, 1, 0), (1, 2, 5), (12, 34, 56)]:
        tag = release_version.format_version(version)
        assert release_version.parse_release_tag(tag) == version


# --- main ----------------------------------------------------------------------------------------

def test_main_first_release(release_version, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _Stdin(""))
    assert release_version.main(["--bump", "minor"]) == 0
    assert capsys.readouterr().out == "0.1.0\n"


def test_main_with_prefix(release_version, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _Stdin("v0.1.0\nv0.2.0\n3.0.0\n"))
    assert release_version.main(["--bump", "minor", "--prefix", "v"]) == 0
    assert capsys.readouterr().out == "0.3.0\n"


def test_main_rejects_unknown_bump(release_version, monkeypatch):
    monkeypatch.setattr("sys.stdin", _Stdin("1.1.2\n"))
    with pytest.raises(SystemExit):
        release_version.main(["--bump", "build"])


def test_main_requires_bump(release_version, monkeypatch):
    monkeypatch.setattr("sys.stdin", _Stdin("1.1.2\n"))
    with pytest.raises(SystemExit):
        release_version.main([])


def test_main_fails_on_malformed_release_tag(release_version, monkeypatch):
    monkeypatch.setattr("sys.stdin", _Stdin("1.1.2\n1.2\n"))
    with pytest.raises(ValueError):
        release_version.main(["--bump", "patch"])
