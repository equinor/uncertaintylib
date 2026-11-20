# Releases and versions

Each release of uncertaintylib is a git tag `MAJOR.MINOR.PATCH` without a prefix, for example
`1.2.0`, the sdist and the wheel on [PyPI](https://pypi.org/project/uncertaintylib/), and a GitHub
release with notes and the same two files attached.

## Version numbers

Versions follow [semantic versioning](https://semver.org/):

| Part | Increased for | Example |
|---|---|---|
| PATCH | a fix that does not change the documented behaviour or any calculated result | 1.2.0 → 1.2.1 |
| MINOR | new functionality that existing code keeps working with | 1.2.0 → 1.3.0 |
| MAJOR | a change that breaks existing code or the documented behaviour | 1.2.0 → 2.0.0 |

Project rule: a change to calculated results - for example a corrected formula, a changed
default, constant or uncertainty model - is at least MINOR, even when it is a correction, so it
never arrives unnoticed in a patch update. Describe the effect on results in the pull request; the
release notes are generated from the pull request titles.

No file in the repository holds the version. [setuptools-scm](https://setuptools-scm.readthedocs.io/)
reads it from the git tag when the package is built or installed and writes it to
`uncertaintylib/_version.py` (not committed), and `uncertaintylib.__version__` reports it:

| Where the package came from | `__version__` |
|---|---|
| PyPI, tag `1.2.0` or its sdist/wheel | `1.2.0` |
| a commit after `1.2.0` | a development version such as `1.2.1.dev3+g1a2b3c4` |
| a source tree without an install | `0+unknown` |

Building from a git checkout needs the tags (a full clone, or `fetch-depth: 0` in a workflow). An
editable install (`pip install -e .`) records the version when it is installed; after pulling new
commits or tags, run `pip install -e .` again to update it. `tests/test_version.py` fails until you
do.

## Making a release

A release is always started by a person; merging or pushing to `main` never releases anything.

1. Make sure every change meant for the release is merged into `main`.
2. On GitHub, open **Actions → Release → Run workflow**, keep the branch `main`, and choose which
   part of the version to increase (`patch`, `minor` or `major`). The workflow works out the new
   version from the highest existing release tag.
3. The workflow, `.github/workflows/release.yml`, runs on the commit `main` pointed at when it was
   started:
   1. **prepare** - stops unless the run is on `main`, works out the version
      (`tools/release_version.py`) and stops if the tag or the version on PyPI already exists.
   2. **test** - the full test workflow, `tests.yml`.
   3. **build** - tags the commit locally (not pushed) so setuptools-scm gives the release version,
      builds the sdist and the wheel once, checks their names, content and metadata
      (`twine check --strict`), installs each into a clean virtual environment and runs the test
      suite against it, and keeps exactly those files with their SHA-256 sums.
   4. **tag** - waits for approval in the environment `release`, then creates the tag at the
      release commit.
   5. **publish** - waits for approval in the environment `pypi`, checks the files against the
      SHA-256 sums, uploads them to PyPI with Trusted Publishing (no PyPI token is stored
      anywhere) and checks that PyPI holds exactly those files.
   6. **github-release** - creates the GitHub release for the tag, with generated notes and the same
      files attached.
4. Edit the release notes on GitHub if the effect on calculated results needs explaining.

So a release needs two approvals: one before the tag is created and one before the upload to PyPI.

## If a release run fails

- Before the **tag** job has run, nothing is published: fix the cause and start a new run.
- From the **tag** job on, use **Re-run failed jobs** in the *same* run. The tag and publish jobs
  accept their own earlier partial work only on a re-run of the same run (same commit, same
  files): an existing tag must point at the release commit, and files already on PyPI must be the
  ones built in that run (same SHA-256, with provenance from this repository's `release.yml`).
- Never start a new run for a version that already has files on PyPI, and never upload by hand.
  PyPI never accepts a file name twice, even after deletion.
- A published tag is never moved or deleted. A mistake is corrected by a new release.

## One-time setup

Settings made once by a repository administrator, before the first release:

- **Environments** - *Settings → Environments*: create `release` and `pypi`, each with *Required
  reviewers* and, under *Deployment branches and tags*, only the branch `main`.
- **Trusted Publisher on PyPI** - on pypi.org, *uncertaintylib → Manage → Publishing*: add a GitHub
  trusted publisher with owner `equinor`, repository `uncertaintylib`, workflow `release.yml` and
  environment `pypi`.
- **Protect release tags** - *Settings → Rules → Rulesets → New tag ruleset*, target
  `refs/tags/[0-9]*`, with *Restrict updates* and *Restrict deletions*. Do not restrict creation,
  as the workflow creates the tag.
