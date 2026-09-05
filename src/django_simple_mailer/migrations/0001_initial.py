import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MailLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        null=True,
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        null=True,
                    ),
                ),
                ("sent", models.BooleanField(default=False)),
                ("error", models.TextField(blank=True, null=True)),
                ("sender", models.CharField(blank=True, max_length=128, null=True)),
                # Stored as a JSON array — works with any Django-supported database.
                ("recipients", models.JSONField(blank=True, null=True)),
                # max_length=998: RFC 2822/5322 §2.1.1 maximum header line length.
                ("subject", models.CharField(blank=True, max_length=998, null=True)),
                ("txt_message", models.TextField(blank=True, null=True)),
                ("html_message", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Mail Log",
                "verbose_name_plural": "Mail Logs",
            },
        ),
    ]
