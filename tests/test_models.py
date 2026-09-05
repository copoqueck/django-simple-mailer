"""
Tests for django_simple_mailer.models — the MailLog model.

These tests require a database (SQLite in-memory, configured in tests/settings.py).
"""

import time

import pytest

from django_simple_mailer.models import MailLog


@pytest.mark.django_db
def test_save_updates_modified_timestamp():
    """MailLog.save() always refreshes the modified timestamp."""
    log = MailLog.objects.create(
        sent=True,
        sender="from@example.com",
        recipients=["to@example.com"],
        subject="Test subject",
    )
    original_modified = log.modified

    time.sleep(0.05)
    log.save()

    assert log.modified > original_modified
