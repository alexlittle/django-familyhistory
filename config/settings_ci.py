# config/settings_ci.py
from config.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
}
SECRET_KEY = "ci-only-not-a-real-secret"
DEBUG = False