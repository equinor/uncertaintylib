#!/usr/bin/env bash
# Installs the wheel and the sdist into clean virtual environments and runs the test suite against
# each of them.
#
# Used by the `package` job of .github/workflows/tests.yml and the `build` job of
# .github/workflows/release.yml, after tools/check_distributions.py:
#
#     bash tools/test_distributions.sh <dist folder> <version>
#
# Each distribution gets its own new virtual environment and is tested with a copy of tests/
# outside the checkout, so the source tree cannot be imported by accident. The sdist is unpacked
# into a folder without .git and installed from there, so its version comes from the PKG-INFO in
# the sdist and not from the git tags. Inside the pytest session, tests/test_installed_package.py
# (enabled by UNCERTAINTYLIB_TEST_INSTALLED) asserts that uncertaintylib is imported from the
# virtual environment and reports <version>.
#
# Needs GITHUB_WORKSPACE (the checkout) and RUNNER_TEMP (a scratch folder outside the checkout).
set -euo pipefail

dist=$(realpath "$1")
version="$2"
work="${RUNNER_TEMP:?}/distribution-test"

export UNCERTAINTYLIB_TEST_INSTALLED=1
export UNCERTAINTYLIB_EXPECTED_VERSION="${version}"
export MPLBACKEND=Agg

rm -rf "${work}"
mkdir -p "${work}/sdist-source"
tar -xzf "${dist}/uncertaintylib-${version}.tar.gz" -C "${work}/sdist-source"
if [ -e "${work}/sdist-source/uncertaintylib-${version}/.git" ]; then
  echo "::error::The unpacked sdist contains .git."
  exit 1
fi

for kind in wheel sdist; do
  if [ "${kind}" = wheel ]; then
    target="${dist}/uncertaintylib-${version}-py3-none-any.whl"
  else
    target="${work}/sdist-source/uncertaintylib-${version}"
  fi
  echo "::group::${kind}: ${target}"
  python -m venv "${work}/venv-${kind}"
  venv_python="${work}/venv-${kind}/bin/python"
  "${venv_python}" -m pip install --upgrade pip
  "${venv_python}" -m pip install "${target}" pytest pvtlib
  cp -r "${GITHUB_WORKSPACE:?}/tests" "${work}/tests-${kind}"
  (cd "${work}/tests-${kind}" && "${venv_python}" -m pytest --import-mode=importlib -p no:cacheprovider -rA .)
  echo "::endgroup::"
done
