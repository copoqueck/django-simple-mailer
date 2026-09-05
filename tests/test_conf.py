"""
Tests for django_simple_mailer.conf — the SIMPLE_MAILER_LOG_EMAILS setting.
"""

from django_simple_mailer.conf import log_emails_enabled


def test_disabled_by_default():
    """Returns False when SIMPLE_MAILER_LOG_EMAILS is not configured."""
    # The setting is absent from tests/settings.py — this covers the true default.
    assert log_emails_enabled() is False


def test_enabled_when_set_to_true(settings):
    settings.SIMPLE_MAILER_LOG_EMAILS = True
    assert log_emails_enabled() is True


def test_disabled_when_set_to_false(settings):
    settings.SIMPLE_MAILER_LOG_EMAILS = False
    assert log_emails_enabled() is False
