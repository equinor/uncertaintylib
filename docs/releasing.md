# Releasing

uncertaintylib is published to [PyPI](https://pypi.org/project/uncertaintylib/) by the workflow
`.github/workflows/build-and-distribute.yml` when a GitHub release is published. The version is
set by hand in `pyproject.toml`.

## Steps

1. **Bump the version.** In a pull request, change `version` in the `[project]` table of
   `pyproject.toml` (for example from `1.1.2` to `1.2.0`) and merge the pull request to `main`
   once the checks pass. `uncertaintylib.__version__` reads the version from the installed
   package metadata, so no other file has to change.
2. **Create the GitHub release.** On GitHub, draft a new release from `main` with a new tag equal
   to the version, for example `1.2.0` (a leading `v`, as in `v1.2.0`, is also accepted), and
   publish it. Saving the release as a draft does not start the workflow; publishing it does.

## What the workflow does

1. **validate** - checks that the release tag, without a leading `v`, equals the version in
   `pyproject.toml`. If not, the run stops and nothing is published. Delete the release and the
   tag, fix the version and start again.
2. **tests** - runs the full test workflow (`tests.yml`) on the release commit: flake8 and the
   test suite on Linux and Windows, the examples, coverage and the `package` job. The `package`
   job builds the sdist and the wheel once, checks them with `twine check --strict`, installs each
   into a clean virtual environment, runs the test suite against the installed package from a
   copy of `tests/` outside the checkout, and keeps the two files as the artifact `dist`.
3. **publish** - downloads exactly those two tested files, checks that their names carry the
   release version, and uploads them to PyPI with `twine`. This is the only job that has access
   to the PyPI token (repository secret `PYPI_TOKEN`).

If any job fails, nothing is uploaded. PyPI does not accept the same version twice, so a failed
upload after a partial success needs a new version number.

## Checks on pull requests

`validate-version.yml` warns on pull requests when the version in `pyproject.toml` does not have
the form `MAJOR.MINOR.PATCH`, or when it equals the latest tag (a reminder to bump it before the
next release).
