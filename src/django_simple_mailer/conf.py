from django.conf import settings


def log_emails_enabled() -> bool:
    """Returns True if email logging to ``MailLog`` is enabled.

    Controlled by ``SIMPLE_MAILER_LOG_EMAILS`` in Django settings.
    Defaults to ``False`` — no database is required when logging is off.
    """
    return bool(getattr(settings, "SIMPLE_MAILER_LOG_EMAILS", False))
