"""Check the file names and the content of the built distributions in a folder.

Used by the ``package`` job of ``.github/workflows/tests.yml`` and the ``build`` job of
``.github/workflows/release.yml``, after ``python -m build``::

    python tools/check_distributions.py dist                    # any version
    python tools/check_distributions.py dist --version 1.2.0    # release build

The folder must hold exactly one sdist and one wheel of uncertaintylib, both of the same version
(and of ``--version`` when given). The wheel must hold exactly the package modules, including the
``_version.py`` that setuptools-scm writes, and the sdist must hold the files needed to build and
test it. The version is printed on standard output, so a workflow can use it; everything else
goes to standard error.
"""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from pathlib import Path

MODULES = {
    "uncertaintylib/__init__.py",
    "uncertaintylib/_version.py",
    "uncertaintylib/plot_functions.py",
    "uncertaintylib/uncertainty_functions.py",
    "uncertaintylib/uncertainty_models/__init__.py",
    "uncertaintylib/uncertainty_models/gas_composition.py",
}
SDIST_FILES = {"pyproject.toml", "README.md", "LICENSE", "PKG-INFO", *MODULES}
WHEEL_NAME = re.compile(r"uncertaintylib-(?P<version>[^-]+)-py3-none-any\.whl")


def _metadata_version(metadata: str) -> str | None:
    """Return the ``Version`` field of a METADATA or PKG-INFO text, or None if it has none.

    Only the header block (up to the first blank line) is read; the line ending may be LF or CRLF.
    """
    for line in metadata.splitlines():
        if not line:
            break
        if line.startswith("Version: "):
            return line[len("Version: "):]
    return None


def check(dist_dir: Path, expected_version: str | None) -> str:
    """Check the distributions in ``dist_dir`` and return their version.

    Raises
    ------
    AssertionError
        If the folder does not hold exactly the expected sdist and wheel, or their content is wrong.
    """
    found = sorted(path.name for path in dist_dir.iterdir())
    wheels = [name for name in found if WHEEL_NAME.fullmatch(name)]
    assert len(wheels) == 1, f"{dist_dir} holds {found}, expected exactly one uncertaintylib wheel"
    version = WHEEL_NAME.fullmatch(wheels[0]).group("version")
    if expected_version is not None:
        assert version == expected_version, f"the wheel has version {version}, expected {expected_version}"

    wheel = f"uncertaintylib-{version}-py3-none-any.whl"
    sdist = f"uncertaintylib-{version}.tar.gz"
    assert found == sorted([wheel, sdist]), f"{dist_dir} holds {found}, expected {sorted([wheel, sdist])}"

    wheel_names = zipfile.ZipFile(dist_dir / wheel).namelist()
    wheel_modules = {name for name in wheel_names if name.endswith(".py")}
    assert wheel_modules == MODULES, f"wheel modules {sorted(wheel_modules)}, expected {sorted(MODULES)}"
    metadata = zipfile.ZipFile(dist_dir / wheel).read(f"uncertaintylib-{version}.dist-info/METADATA")
    metadata_version = _metadata_version(metadata.decode("utf-8"))
    assert metadata_version == version, f"wheel METADATA has version {metadata_version}, expected {version}"

    root = f"uncertaintylib-{version}/"
    with tarfile.open(dist_dir / sdist) as archive:
        sdist_names = set(archive.getnames())
        pkg_info = archive.extractfile(root + "PKG-INFO").read().decode("utf-8")
    missing = {root + name for name in SDIST_FILES} - sdist_names
    assert not missing, f"sdist lacks {sorted(missing)}"
    pkg_info_version = _metadata_version(pkg_info)
    assert pkg_info_version == version, f"sdist PKG-INFO has version {pkg_info_version}, expected {version}"

    print("wheel:", *sorted(wheel_names), sep="\n  ", file=sys.stderr)
    print("sdist:", *sorted(sdist_names), sep="\n  ", file=sys.stderr)
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument("--version", help="the version the distributions must have")
    args = parser.parse_args(argv)
    print(check(args.dist_dir, args.version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
