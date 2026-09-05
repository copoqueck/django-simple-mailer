"""
Tests for django_simple_mailer.base — the Email class and MailerError.

All tests are pure unit tests: send_mail and render_to_string are mocked
so no SMTP connection or real templates are needed. MailLog is also mocked
so no database is required here; see test_models.py for model-level tests.
"""

from unittest.mock import patch

import pytest

from django_simple_mailer import Email, MailerError

# A fixed string returned by all render_to_string mocks.
RENDERED = "mock_rendered_content"


@pytest.fixture
def email():
    return Email(
        template="test_email",
        context={"key": "value"},
        recipients=["to@example.com"],
    )


# ---------------------------------------------------------------------------
# Subject rendering
# ---------------------------------------------------------------------------


@patch("django_simple_mailer.base.render_to_string", return_value="line one\r\nline two\n")
def test_subject_strips_newlines(mock_render):
    email = Email(template="t", context={}, recipients=[])
    assert email.subject == "line oneline two"


# ---------------------------------------------------------------------------
# send() — success path
# ---------------------------------------------------------------------------


@patch("django_simple_mailer.base.render_to_string", return_value=RENDERED)
@patch("django_simple_mailer.base.send_mail")
def test_send_calls_send_mail_with_correct_args(mock_send_mail, mock_render, email):
    email.send()

    mock_send_mail.assert_called_once_with(
        from_email="from@example.com",
        subject=RENDERED,
        message=RENDERED,
        html_message=RENDERED,
        recipient_list=["to@example.com"],
        fail_silently=False,
    )


# ---------------------------------------------------------------------------
# send() — failure path
# ---------------------------------------------------------------------------


@patch("django_simple_mailer.base.render_to_string", return_value=RENDERED)
@patch("django_simple_mailer.base.send_mail", side_effect=ConnectionError("SMTP unreachable"))
def test_send_raises_mailer_error_on_failure(mock_send_mail, mock_render, email):
    with pytest.raises(MailerError) as exc_info:
        email.send()

    # Original exception is preserved as __cause__ for debugging.
    assert isinstance(exc_info.value.__cause__, ConnectionError)
    assert "SMTP unreachable" in str(exc_info.value.__cause__)


# ---------------------------------------------------------------------------
# send() — logging disabled (default)
# ---------------------------------------------------------------------------


@patch("django_simple_mailer.base.render_to_string", return_value=RENDERED)
@patch("django_simple_mailer.base.send_mail")
def test_send_does_not_write_log_when_disabled(mock_send_mail, mock_render, email):
    # SIMPLE_MAILER_LOG_EMAILS is absent from test settings → defaults to False.
    with patch.object(email, "_write_log") as mock_write_log:
        email.send()
    mock_write_log.assert_not_called()


# ---------------------------------------------------------------------------
# send() — logging enabled
# ---------------------------------------------------------------------------


@patch("django_simple_mailer.base.render_to_string", return_value=RENDERED)
@patch("django_simple_mailer.base.send_mail")
def test_send_writes_success_log_when_enabled(mock_send_mail, mock_render, email, settings):
    settings.SIMPLE_MAILER_LOG_EMAILS = True

    with patch("django_simple_mailer.models.MailLog") as mock_log:
        email.send()

    mock_log.objects.create.assert_called_once_with(
        sender="from@example.com",
        recipients=["to@example.com"],
        subject=RENDERED,
        txt_message=RENDERED,
        html_message=RENDERED,
        sent=True,
        error=None,
    )


@patch("django_simple_mailer.base.render_to_string", return_value=RENDERED)
@patch("django_simple_mailer.base.send_mail", side_effect=ConnectionError("SMTP unreachable"))
def test_send_writes_failure_log_when_enabled(mock_send_mail, mock_render, email, settings):
    settings.SIMPLE_MAILER_LOG_EMAILS = True

    with patch("django_simple_mailer.models.MailLog") as mock_log, pytest.raises(MailerError):
        email.send()

    mock_log.objects.create.assert_called_once_with(
        sender="from@example.com",
        recipients=["to@example.com"],
        subject=RENDERED,
        txt_message=RENDERED,
        html_message=RENDERED,
        sent=False,
        error="SMTP unreachable",
    )
