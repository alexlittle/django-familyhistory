# config/settings_docs.py
"""Settings used only to build the Sphinx documentation.

Sphinx's autodoc needs `django.setup()` to succeed so it can import
`familyhistory`/`api` modules, but the real `config/local_settings.py` is
gitignored (it holds the production DB credentials and secret key) and isn't
available on Read the Docs. The docs build never opens a database connection,
so these are throwaway values good only for populating Django's app registry.
"""

from config.settings import *  # NOSONAR

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SECRET_KEY = "docs-build-not-a-real-secret"
DEBUG = False
ALLOWED_HOSTS = ["*"]
