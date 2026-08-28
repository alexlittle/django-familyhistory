# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import tomllib
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
BASE_DIR = DOCS_DIR.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docs")

import django

django.setup()

with (BASE_DIR / "pyproject.toml").open("rb") as f:
    _pyproject = tomllib.load(f)["project"]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = _pyproject["name"]
copyright = "Alex Little"
author = _pyproject["authors"][0]["name"]
release = _pyproject["version"]
version = release

# -- General configuration ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc / Napoleon -------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"
autodoc_mock_imports = ["MySQLdb"]

# Docstrings in this project follow the Google style (matches the `pydoclint`
# config in pyproject.toml).
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

# -- Options for HTML output --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
