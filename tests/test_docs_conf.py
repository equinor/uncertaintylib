"""Tests for the documentation configuration, docs/conf.py, and for the completeness of the examples.

Every example folder must have a README.md, and every example script and notebook must appear on
the generated example pages. The other tests check the generated example pages and the rewriting
of relative Markdown links for the documentation site.

These tests check the repository layout, not the package. They are skipped when the test suite runs
against an installed distribution from a copy of tests/ (UNCERTAINTYLIB_TEST_INSTALLED=1), where
docs/ and examples/ are not available.
"""

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("UNCERTAINTYLIB_TEST_INSTALLED") == "1",
                                reason="checks the repository layout, not the installed package")

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/equinor/uncertaintylib"
README = REPOSITORY_ROOT / "README.md"
EXAMPLES_DIR = REPOSITORY_ROOT / "examples"


@pytest.fixture(scope="module")
def docs_conf():
    spec = importlib.util.spec_from_file_location("docs_conf", REPOSITORY_ROOT / "docs" / "conf.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- Completeness of the examples ------------------------------------------------------------------

def test_every_example_folder_has_a_readme():
    folders = [folder for folder in EXAMPLES_DIR.iterdir() if folder.is_dir()]
    assert folders, "no example folders found"
    missing = sorted(folder.name for folder in folders if not (folder / "README.md").is_file())
    assert missing == [], f"example folders without README.md: {missing}"


def test_every_example_script_and_notebook_is_on_a_generated_page(docs_conf):
    items = sorted(path for path in EXAMPLES_DIR.glob("*/*") if path.suffix in (".py", ".ipynb"))
    assert items, "no example scripts or notebooks found"
    pages = {folder: docs_conf.example_page(folder) for folder in docs_conf.example_folders()}
    for item in items:
        page = pages[item.parent]
        if item.suffix == ".py":
            reference = f"```{{literalinclude}} ../../examples/{item.parent.name}/{item.name}"
        else:
            reference = f"{docs_conf.example_page_name(item.parent)}/{item.stem}"
        assert reference in page.splitlines(), f"{item.relative_to(EXAMPLES_DIR)} is not on its example page"


def test_every_example_folder_is_in_the_examples_index(docs_conf):
    folders = docs_conf.example_folders()
    index = docs_conf.examples_index_page(folders).splitlines()
    for folder in EXAMPLES_DIR.iterdir():
        if folder.is_dir():
            assert docs_conf.example_page_name(folder) in index


# --- Example pages ---------------------------------------------------------------------------------

def test_example_page_name(docs_conf):
    assert docs_conf.example_page_name(Path("06 - Gas metering station (Jupyter)")) == \
        "06-gas-metering-station-jupyter"
    assert docs_conf.example_page_name(Path("01 - Simple uncertainty with multiple outputs")) == \
        "01-simple-uncertainty-with-multiple-outputs"
    assert docs_conf.example_page_name(Path("single")) == "single"


def test_example_page_lists_readme_notebooks_and_scripts(docs_conf, tmp_path):
    folder = tmp_path / "10 - New example"
    folder.mkdir()
    (folder / "README.md").write_text("# 10 New example\n", encoding="utf-8")
    (folder / "b_second.py").write_text("", encoding="utf-8")
    (folder / "a_first.py").write_text("", encoding="utf-8")
    (folder / "notebook.ipynb").write_text("{}", encoding="utf-8")
    (folder / "data.csv").write_text("", encoding="utf-8")

    expected = "\n".join([
        "```{include} ../../examples/10 - New example/README.md",
        "```",
        "",
        "## Notebooks",
        "",
        "```{toctree}",
        ":maxdepth: 1",
        "",
        "10-new-example/notebook",
        "```",
        "",
        "## Source code",
        "",
        "```{literalinclude} ../../examples/10 - New example/a_first.py",
        ":caption: a_first.py",
        ":language: python",
        "```",
        "",
        "```{literalinclude} ../../examples/10 - New example/b_second.py",
        ":caption: b_second.py",
        ":language: python",
        "```",
        "",
    ])
    assert docs_conf.example_page(folder) == expected


def test_write_example_pages_copies_notebooks_and_removes_stale_pages(docs_conf, tmp_path, monkeypatch):
    examples_dir = tmp_path / "examples"
    for name in ["01 - First", "02 - Second"]:
        (examples_dir / name).mkdir(parents=True)
        (examples_dir / name / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    (examples_dir / "02 - Second" / "nb.ipynb").write_text("{}", encoding="utf-8")
    pages_dir = tmp_path / "_examples"
    (pages_dir / "03-removed").mkdir(parents=True)
    (pages_dir / "03-removed.md").write_text("old", encoding="utf-8")
    monkeypatch.setattr(docs_conf, "EXAMPLES_DIR", examples_dir)
    monkeypatch.setattr(docs_conf, "EXAMPLE_PAGES_DIR", pages_dir)

    docs_conf.write_example_pages(app=None)

    assert sorted(path.name for path in pages_dir.iterdir()) == \
        ["01-first.md", "02-second", "02-second.md", "index.md"]
    assert [path.name for path in (pages_dir / "02-second").iterdir()] == ["nb.ipynb"]
    assert (pages_dir / "02-second.md").read_text(encoding="utf-8") == \
        docs_conf.example_page(examples_dir / "02 - Second")


# --- Link rewriting --------------------------------------------------------------------------------

def test_link_to_repository_file_points_at_github(docs_conf):
    text = "[License](LICENSE)"
    assert docs_conf.link_repository_files(text, README) == f"[License]({REPOSITORY_URL}/tree/main/LICENSE)"


def test_link_to_examples_folder_points_at_examples_index(docs_conf):
    text = "See the [`examples/`](examples) folder"
    assert docs_conf.link_repository_files(text, README) == \
        "See the [`examples/`](project:/_examples/index.md) folder"


def test_link_to_example_folder_points_at_its_page(docs_conf):
    text = "[Example 06](examples/06%20-%20Gas%20metering%20station%20%28Jupyter%29)"
    assert docs_conf.link_repository_files(text, README) == \
        "[Example 06](project:/_examples/06-gas-metering-station-jupyter.md)"


def test_link_between_example_folders_points_at_the_example_page(docs_conf):
    readme = EXAMPLES_DIR / "04 - Combined uncertainty calculation" / "README.md"
    text = "[Example 03](../03%20-%20Orifice%20meter%20with%20visualization)"
    assert docs_conf.link_repository_files(text, readme) == \
        "[Example 03](project:/_examples/03-orifice-meter-with-visualization.md)"


def test_link_to_uncertainty_models_readme_points_at_its_page(docs_conf):
    text = "[models](uncertaintylib/uncertainty_models/README.md)"
    assert docs_conf.link_repository_files(text, README) == "[models](project:/uncertainty_models.md)"


def test_link_to_documentation_page_is_unchanged(docs_conf):
    text = "[releasing](docs/releasing.md)"
    assert docs_conf.link_repository_files(text, README) == text


def test_external_anchor_mailto_project_missing_and_outside_links_are_unchanged(docs_conf):
    text = ("[a](https://pypi.org/project/uncertaintylib/) [b](#license) [c](mailto:x@example.com) "
            "[d](project:/api.rst) [e](no_such_file.txt) [f](..)")
    assert docs_conf.link_repository_files(text, README) == text


def test_text_without_links_is_unchanged(docs_conf):
    text = "U = k * u (k=2), see section (Notes)."
    assert docs_conf.link_repository_files(text, README) == text
