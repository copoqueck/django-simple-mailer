import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .conf import log_emails_enabled

logger = logging.getLogger(__name__)


class MailerError(Exception):
    """Raised when an email fails to send.

    Wraps the underlying transport exception so callers can catch mailer
    failures without depending on the specific mail backend in use::

        from django_simple_mailer import Email, MailerError

        try:
            Email(template="welcome", context={...}, recipients=[...]).send()
        except MailerError as exc:
            # handle or re-raise
            logger.error("Delivery failed: %s", exc.__cause__)
    """


class Email:
    """Builds and sends a template-driven email.

    Resolves three template files for the given *template* name via
    Django's template engine (``APP_DIRS = True`` is the standard setup —
    templates live in any app's ``templates/`` directory):

    - ``<template>.subject`` — rendered as a single-line subject string
    - ``<template>.txt``     — plain-text body
    - ``<template>.html``    — HTML body

    Usage::

        from django_simple_mailer import Email

        Email(
            template="welcome_email",
            context={"name": "Jane", "link": "https://..."},
            recipients=["jane@example.com"],
        ).send()

    Args:
        template:   Template name (without extension). Must resolve to
                    ``.subject``, ``.txt``, and ``.html`` variants.
        context:    Dict passed to all three template variants.
        recipients: List of email addresses to send to.

    Raises:
        MailerError: if the email cannot be delivered. The original
            exception is available as ``__cause__``.

    Note:
        Enable ``SIMPLE_MAILER_LOG_EMAILS = True`` in Django settings to
        persist every send attempt (success or failure) to the ``MailLog``
        table. See the README for details.
    """

    def __init__(self, template: str, context: dict, recipients: list[str]) -> None:
        self.template = str(template)
        self.recipients = list(recipients)
        self.context = context

    @property
    def subject(self) -> str:
        """Rendered subject line (newlines stripped)."""
        return render_to_string(f"{self.template}.subject", self.context).replace("\n", "").replace("\r", "")

    @property
    def txt_message(self) -> str:
        """Rendered plain-text body."""
        return render_to_string(f"{self.template}.txt", self.context)

    @property
    def html_message(self) -> str:
        """Rendered HTML body."""
        return render_to_string(f"{self.template}.html", self.context)

    def send(self) -> None:
        """Send the email.

        On success, writes a ``MailLog`` record when
        ``SIMPLE_MAILER_LOG_EMAILS = True`` is set in Django settings.
        On failure, logs the error, optionally writes a failed ``MailLog``
        record, and raises :exc:`MailerError`.

        Raises:
            MailerError: wraps any exception raised by the mail backend.
        """
        try:
            send_mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                subject=self.subject,
                message=self.txt_message,
                html_message=self.html_message,
                recipient_list=self.recipients,
                fail_silently=False,
            )
        except Exception as exc:
            logger.error(
                "Failed to send email (template=%r, recipients=%r): %s",
                self.template,
                self.recipients,
                exc,
            )
            if log_emails_enabled():
                self._write_log(sent=False, error=str(exc))
            raise MailerError(f"Failed to send email to {self.recipients}") from exc

        if log_emails_enabled():
            self._write_log(sent=True, error=None)

    def _write_log(self, *, sent: bool, error: str | None) -> None:
        # Deferred import so the model is only loaded when logging is enabled.
        # This keeps the library usable in projects without a database when
        # SIMPLE_MAILER_LOG_EMAILS is False (the default).
        from .models import MailLog

        MailLog.objects.create(
            sender=settings.DEFAULT_FROM_EMAIL,
            recipients=self.recipients,
            subject=self.subject,
            txt_message=self.txt_message,
            html_message=self.html_message,
            sent=sent,
            error=error,
        )
