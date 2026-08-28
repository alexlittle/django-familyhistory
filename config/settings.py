"""
Django settings for django-familyhistory project.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

ADMINS = ()

SITE_ID = 1

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "tinymce",
    "rest_framework",
    "sorl.thumbnail",
    "familyhistory",
    "api",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


#####################################################################
# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

#####################################################################


#####################################################################
# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

#####################################################################


#####################################################################
# Static assets & media uploads
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "..", "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "..", "media")
#####################################################################


#####################################################################
# Email not configured as not used
#####################################################################


#####################################################################
# Authentication
LOGIN_URL = "/admin/login/"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
#####################################################################


#####################################################################
# Security
# Secure-cookie flags are safe as a shared default: they only affect
# the Set-Cookie header, so they don't break local dev (Makefile serves
# dev over HTTPS via runserver_plus) or the test client. Override to
# False in local_settings.py only if an environment genuinely serves
# plain HTTP.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Deliberately NOT enabled by default here: SECURE_SSL_REDIRECT would
# 301-redirect every request, which breaks the Django test client (it
# issues plain HTTP requests) and this settings module doubles as the
# test settings (see pyproject.toml [tool.pytest.ini_options]). HSTS is
# similarly deployment-specific — the browser caches it for the given
# duration regardless of this app. Set both explicitly in the
# production local_settings.py, e.g.:
#   SECURE_SSL_REDIRECT = True
#   SECURE_HSTS_SECONDS = 31536000
#   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#   SECURE_HSTS_PRELOAD = True
#####################################################################


#####################################################################
# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s",
        },
        "simple": {
            "format": "%(levelname)s %(asctime)s %(module)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "familyhistory": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
#####################################################################

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SESSION_COOKIE_NAME = "familyhistory"

TINYMCE_DEFAULT_CONFIG = {
    "height": "500px",
    "width": "960px",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
}

TREE_START_PERSON_ID = None

try:
    from config.local_settings import *  # NOSONAR
except ImportError:
    import warnings

    warnings.warn(
        "Using default settings. Add `config/local_settings.py` for custom settings."
    )
