from django.contrib import admin

from .models import MailLog


@admin.register(MailLog)
class MailLogAdmin(admin.ModelAdmin):
    """Read-only admin view of the email audit log.

    Visible when ``SIMPLE_MAILER_LOG_EMAILS = True`` and
    ``django_simple_mailer`` is in ``INSTALLED_APPS``.

    Add and delete actions are intentionally disabled — ``MailLog`` is a
    historical record and should not be modified or removed via admin.
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    ordering = ("-created",)
    search_fields = ("id", "recipients", "subject")
    list_display = ("id", "created", "recipients", "subject", "sent")

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "id",
                    "created",
                    "sent",
                    "error",
                    "sender",
                    "recipients",
                    "subject",
                    "txt_message",
                    "html_message",
                ],
            },
        ),
    )
    readonly_fields = [
        "id",
        "created",
        "sent",
        "error",
        "sender",
        "recipients",
        "subject",
        "txt_message",
        "html_message",
    ]
