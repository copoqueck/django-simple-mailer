"""
Minimal Django settings for the django-simple-mailer test suite.

SIMPLE_MAILER_LOG_EMAILS is intentionally absent here so that tests can
verify the library's default behaviour (disabled) without any override.
Tests that need logging enabled set it explicitly via the `settings` fixture.
"""

SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django_simple_mailer",
]

DEFAULT_FROM_EMAIL = "from@example.com"

# APP_DIRS is False because all template rendering is mocked in unit tests.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {},
    }
]
