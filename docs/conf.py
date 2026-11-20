# Sphinx configuration of the uncertaintylib documentation site.
#
# The site is assembled from files that are maintained for their own sake:
# - README.md is the landing page,
# - uncertaintylib/uncertainty_models/README.md is the page on the uncertainty models,
# - every folder in examples/ becomes an example page (its README, its scripts and its notebooks),
# - the API reference is generated from the NumPy-style docstrings of the package.
#
# Build locally with:
#     pip install -e .[docs]
#     sphinx-build -W --keep-going -b html docs docs/_build/html

from __future__ import annotations

import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote

import uncertaintylib

DOCS_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = DOCS_DIR.parent
REPOSITORY_URL = "https://github.com/equinor/uncertaintylib"

project = "uncertaintylib"
author = "Equinor"
copyright = "Equinor ASA"
release = uncertaintylib.__version__
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "myst_nb",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}
exclude_patterns = ["_build"]

# --- API reference ----------------------------------------------------------------------------------
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False

# --- Markdown and notebooks ---------------------------------------------------------------------------
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
]
myst_heading_anchors = 3
# The notebooks are shown with the outputs stored in them; they are not run during the build.
# The `examples` job of tests.yml runs them.
nb_execution_mode = "off"
# The example notebooks are written for Jupyter, where a jump in heading level (for example from
# "#" to "###") is common and harmless. MyST reports it as a warning, which -W would turn into an
# error, so that warning category is not reported.
suppress_warnings = ["myst.header"]

# --- HTML -------------------------------------------------------------------------------------------
html_theme = "furo"
html_title = f"{project} {release}"

# --- Example pages ----------------------------------------------------------------------------------
# docs/_examples/ is generated at the start of every build and is not kept in git. For each example
# folder it holds one page (<page name>.md) and a folder <page name>/ with copies of the notebooks,
# which MyST-NB renders as pages of their own.
EXAMPLES_DIR = REPOSITORY_ROOT / "examples"
EXAMPLE_PAGES_DIR = DOCS_DIR / "_examples"

# Repository Markdown files that are documentation pages of their own, and the page that shows them.
DOCUMENT_PAGES = {
    REPOSITORY_ROOT / "uncertaintylib" / "uncertainty_models" / "README.md": "uncertainty_models.md",
}


def example_folders():
    """Example folders: the subfolders of examples/, in name order.

    Returns
    -------
    list of pathlib.Path
        Absolute paths of the example folders.
    """
    return sorted(folder for folder in EXAMPLES_DIR.iterdir() if folder.is_dir())


def example_page_name(example_folder):
    """Page name of an example folder.

    Runs of characters other than letters and digits become a single hyphen, and the name is
    lower case, e.g. '06 - Gas metering station (Jupyter)' -> '06-gas-metering-station-jupyter'.

    Parameters
    ----------
    example_folder : pathlib.Path
        Path of the example folder.

    Returns
    -------
    str
    """
    return re.sub(r"[^a-z0-9]+", "-", example_folder.name.lower()).strip("-")


def example_scripts(example_folder):
    """Python scripts of an example folder, in name order."""
    return sorted(example_folder.glob("*.py"))


def example_notebooks(example_folder):
    """Jupyter notebooks of an example folder, in name order."""
    return sorted(example_folder.glob("*.ipynb"))


def example_page(example_folder):
    """Markdown source of the page of one example.

    The page includes the README of the example, lists its notebooks (each rendered as its own
    page from a copy in docs/_examples/<page name>/) and shows the source of each script.

    Parameters
    ----------
    example_folder : pathlib.Path
        Absolute path of the example folder.

    Returns
    -------
    str
        Markdown for docs/_examples/<page name>.md; paths in it are relative to docs/_examples/.
    """
    folder = "../../examples/" + example_folder.name
    lines = [f"```{{include}} {folder}/README.md", "```", ""]
    notebooks = example_notebooks(example_folder)
    if notebooks:
        lines += ["## Notebooks", "", "```{toctree}", ":maxdepth: 1", ""]
        lines += [f"{example_page_name(example_folder)}/{notebook.stem}" for notebook in notebooks]
        lines += ["```", ""]
    scripts = example_scripts(example_folder)
    if scripts:
        lines += ["## Source code", ""]
        for script in scripts:
            lines += [f"```{{literalinclude}} {folder}/{script.name}",
                      f":caption: {script.name}",
                      ":language: python",
                      "```",
                      ""]
    return "\n".join(lines)


def examples_index_page(folders):
    """Markdown source of the examples overview page: examples/README.md and a hidden toctree.

    Parameters
    ----------
    folders : list of pathlib.Path
        Example folders, in the order they are listed.

    Returns
    -------
    str
        Markdown for docs/_examples/index.md.
    """
    lines = ["```{include} ../../examples/README.md", "```", "", "```{toctree}", ":hidden:", ""]
    lines += [example_page_name(folder) for folder in folders]
    lines += ["```", ""]
    return "\n".join(lines)


def _write_if_changed(path, content):
    if not path.exists() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def write_example_pages(app):
    """Regenerate docs/_examples/ from examples/.

    Pages are only rewritten when their content changes, so an incremental build stays
    incremental. Pages and notebook copies of examples that no longer exist are removed.
    """
    folders = example_folders()
    pages = {"index.md": examples_index_page(folders)}
    for folder in folders:
        pages[example_page_name(folder) + ".md"] = example_page(folder)

    EXAMPLE_PAGES_DIR.mkdir(exist_ok=True)
    notebook_dirs = {example_page_name(folder) for folder in folders if example_notebooks(folder)}
    for old in EXAMPLE_PAGES_DIR.iterdir():
        if old.is_dir() and old.name not in notebook_dirs:
            shutil.rmtree(old)
        elif old.is_file() and old.name not in pages:
            old.unlink()
    for name, content in pages.items():
        _write_if_changed(EXAMPLE_PAGES_DIR / name, content)

    for folder in folders:
        notebooks = example_notebooks(folder)
        if not notebooks:
            continue
        copy_dir = EXAMPLE_PAGES_DIR / example_page_name(folder)
        copy_dir.mkdir(exist_ok=True)
        names = {notebook.name for notebook in notebooks}
        for old in copy_dir.iterdir():
            if old.name not in names:
                old.unlink()
        for notebook in notebooks:
            copy = copy_dir / notebook.name
            if not copy.exists() or copy.read_bytes() != notebook.read_bytes():
                shutil.copyfile(notebook, copy)


# --- Links in Markdown written for GitHub -------------------------------------------------------------
# README.md and the other Markdown files are written to be read on GitHub, so their relative links
# point at repository files and folders. On the site, links to example folders go to the example
# pages, links to Markdown files that are shown as pages go to those pages, and links to any other
# repository file go to the file on GitHub. Links between pages in docs/ are left to Sphinx.
_MARKDOWN_LINK = re.compile(r"\]\((?P<target>[^)\s]+)\)")


def link_repository_files(markdown_text, markdown_file):
    """Rewrite the relative links of a Markdown text for the documentation site.

    Parameters
    ----------
    markdown_text : str
        Markdown source.
    markdown_file : pathlib.Path
        Absolute path of the file the text comes from; relative links are resolved against it.

    Returns
    -------
    str
        The text with relative links to existing repository files and folders replaced:

        - examples/ -> ``project:/_examples/index.md``
        - an example folder -> ``project:/_examples/<page name>.md``
        - a file in DOCUMENT_PAGES -> ``project:/<page>``
        - a Markdown or reStructuredText file in docs/ -> unchanged
        - any other repository file or folder -> its URL on GitHub (main branch)

        External URLs, anchors, ``mailto:`` and ``project:`` links, links that leave the
        repository and links to paths that do not exist are left unchanged.
    """
    folders = example_folders()

    def replace(match):
        target = match["target"]
        if "://" in target or target.startswith(("#", "mailto:", "project:")):
            return match[0]
        resolved = (markdown_file.parent / unquote(target.split("#", 1)[0])).resolve()
        if not resolved.exists() or not resolved.is_relative_to(REPOSITORY_ROOT):
            return match[0]
        if resolved.is_relative_to(DOCS_DIR) and resolved.suffix in source_suffix:
            return match[0]
        if resolved == EXAMPLES_DIR:
            return "](project:/_examples/index.md)"
        if resolved in folders:
            return f"](project:/_examples/{example_page_name(resolved)}.md)"
        if resolved in DOCUMENT_PAGES:
            return f"](project:/{DOCUMENT_PAGES[resolved]})"
        relative = resolved.relative_to(REPOSITORY_ROOT).as_posix()
        return f"]({REPOSITORY_URL}/tree/main/{quote(relative)})"

    return _MARKDOWN_LINK.sub(replace, markdown_text)


def _on_include_read(app, relative_path, parent_docname, content):
    included_file = (Path(app.srcdir) / relative_path).resolve()
    if included_file.suffix == ".md":
        content[0] = link_repository_files(content[0], included_file)


def _on_source_read(app, docname, source):
    source_file = Path(app.env.doc2path(docname)).resolve()
    if source_file.suffix == ".md":
        source[0] = link_repository_files(source[0], source_file)


def setup(app):
    app.connect("builder-inited", write_example_pages)
    app.connect("include-read", _on_include_read)
    app.connect("source-read", _on_source_read)
