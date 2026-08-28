# Generate with:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = "*****************************"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "****",
        "USER": "****",
        "PASSWORD": "****",
        "HOST": "",
        "PORT": "",
    }
}

DEBUG = False

ALLOWED_HOSTS = []

# For a real production deployment served only over HTTPS, also set:
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
