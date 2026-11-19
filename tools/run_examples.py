"""Run every example script and notebook in examples/ headless, and report which ones fail.

The examples folder is copied to a work folder first and everything runs from that copy, so
nothing is written back into the repository. Scripts run with ``python <script>`` from their own
folder; notebooks are executed with nbclient from their own folder and are not saved. matplotlib
uses the non-interactive Agg backend. Each item runs in its own process with a time limit.

Usage::

    python tools/run_examples.py --work-dir <new or empty folder> [--timeout-seconds 900]
        [--expected-failure "<example folder>/<file>" ...]

An item given with ``--expected-failure`` is a known, reported defect: it is still run, and its
failure is reported as XFAIL. If it succeeds it is reported as XPASS and counts as a failure, so
the entry has to be removed as soon as the defect is fixed.

Exit code 0 when every item succeeded (or failed as expected), 1 otherwise.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPOSITORY_ROOT / "examples"

# Executes one notebook in its own folder without saving it. Run as a separate process so that
# the per-item time limit also covers kernel start-up and shutdown.
_NOTEBOOK_RUNNER = """
import sys
import nbformat
from nbclient import NotebookClient
notebook_path, timeout_seconds, folder = sys.argv[1], int(sys.argv[2]), sys.argv[3]
notebook = nbformat.read(notebook_path, as_version=4)
client = NotebookClient(notebook, timeout=timeout_seconds, kernel_name="python3",
                        resources={"metadata": {"path": folder}})
client.execute()
"""


def find_example_items(examples_dir):
    """Example scripts and notebooks, in folder and file name order.

    Parameters
    ----------
    examples_dir : pathlib.Path
        Folder holding one subfolder per example.

    Returns
    -------
    list of pathlib.Path
        Paths of the ``*.py`` and ``*.ipynb`` files in the example subfolders.
    """
    items = []
    for folder in sorted(path for path in examples_dir.iterdir() if path.is_dir()):
        items += sorted(path for path in folder.iterdir()
                        if path.suffix in (".py", ".ipynb") and path.is_file())
    return items


def command_for(item, timeout_seconds):
    """Command line that runs one example item with the current Python interpreter.

    Parameters
    ----------
    item : pathlib.Path
        Script (``.py``) or notebook (``.ipynb``).
    timeout_seconds : int
        Time limit in seconds, passed to the notebook client as its per-cell limit.

    Returns
    -------
    list of str
    """
    if item.suffix == ".py":
        return [sys.executable, item.name]
    return [sys.executable, "-c", _NOTEBOOK_RUNNER, item.name, str(timeout_seconds), str(item.parent)]


def outcome(succeeded, expected_failure):
    """Outcome label of one item and whether it counts as a failure of the run.

    Parameters
    ----------
    succeeded : bool
        Whether the item ran without error within its time limit.
    expected_failure : bool
        Whether the item is listed as a known failure.

    Returns
    -------
    tuple of (str, bool)
        Label ``OK``, ``FAIL``, ``XFAIL`` or ``XPASS``, and True when the run must fail.
    """
    if expected_failure:
        return ("XPASS", True) if succeeded else ("XFAIL", False)
    return ("OK", False) if succeeded else ("FAIL", True)


def run_examples(work_dir, timeout_seconds):
    """Copy examples/ into ``work_dir`` and run every item there.

    Parameters
    ----------
    work_dir : pathlib.Path
        Folder to copy the examples into. Must not exist or be empty.
    timeout_seconds : int
        Time limit per item, in seconds.

    Returns
    -------
    list of tuple
        ``(relative path, succeeded, duration in seconds)`` per item.
    """
    if work_dir.exists() and any(work_dir.iterdir()):
        raise SystemExit(f"work folder {work_dir} is not empty")
    examples_copy = work_dir / "examples"
    shutil.copytree(EXAMPLES_DIR, examples_copy)

    environment = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
    results = []
    for item in find_example_items(examples_copy):
        name = item.relative_to(examples_copy).as_posix()
        print(f"::group::{name}", flush=True)
        start = time.perf_counter()
        try:
            completed = subprocess.run(command_for(item, timeout_seconds), cwd=item.parent,
                                       env=environment, timeout=timeout_seconds)
            succeeded = completed.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"timed out after {timeout_seconds} s", flush=True)
            succeeded = False
        duration = time.perf_counter() - start
        print("::endgroup::", flush=True)
        print(f"{'ran' if succeeded else 'FAILED'} in {duration:.1f} s: {name}", flush=True)
        results.append((name, succeeded, duration))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work-dir", required=True, type=Path,
                        help="folder to copy examples/ into and run from (must be new or empty)")
    parser.add_argument("--timeout-seconds", type=int, default=900,
                        help="time limit per script or notebook, in seconds (default 900)")
    parser.add_argument("--expected-failure", action="append", default=[],
                        help="'<example folder>/<file>' of a known failing item (repeatable)")
    arguments = parser.parse_args()

    results = run_examples(arguments.work_dir.resolve(), arguments.timeout_seconds)
    if not results:
        print("No example scripts or notebooks found.")
        return 1
    unknown = sorted(set(arguments.expected_failure) - {name for name, _, _ in results})
    if unknown:
        print(f"--expected-failure names items that do not exist: {', '.join(unknown)}")
        return 1

    print("\nSummary")
    unexpected = []
    for name, succeeded, duration in results:
        label, fails_run = outcome(succeeded, name in arguments.expected_failure)
        print(f"  {label:5} {duration:7.1f} s  {name}")
        if fails_run:
            unexpected.append(f"{name} ({label})")
    if unexpected:
        print(f"\n{len(unexpected)} of {len(results)} examples did not behave as expected: "
              f"{', '.join(unexpected)}")
        print("XPASS means a listed known failure now runs: remove it from --expected-failure.")
        return 1
    print(f"\nAll {len(results)} examples behaved as expected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
