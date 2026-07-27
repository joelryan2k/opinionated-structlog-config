"""Minimal Django settings so the Django/request tests can run."""

SECRET_KEY = "test-secret-key"

DEBUG = True

ALLOWED_HOSTS = ["testserver", "localhost"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_structlog",
]

# RequestMiddleware must already be installed for the live-request test. The
# django-config test exercises the *appending* behaviour on its own list.
MIDDLEWARE = [
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "tests.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

# Consumed by celery.py's setup_logging receiver.
OPINIONATED_STRUCTLOG_CONFIG = {}
