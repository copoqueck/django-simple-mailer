# django-simple-mailer

A simple Django app for sending template-driven emails.

## Features

- Send HTML + plain-text emails using Django templates
- **Optional email logging** — persist every send attempt to a `MailLog` table, viewable in Django admin (disabled by default, enable with `SIMPLE_MAILER_LOG_EMAILS = True`)
- Clean `MailerError` exception for straightforward error handling

---

## Installation

```bash
pip install django-simple-mailer
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_simple_mailer",
]
```

Configure Django's email settings (standard Django — nothing library-specific):

```python
DEFAULT_FROM_EMAIL = "no-reply@example.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.example.com"
EMAIL_HOST_USER = "..."
EMAIL_HOST_PASSWORD = "..."
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

Ensure your `TEMPLATES` setting has `APP_DIRS` enabled — this is how the mailer finds your email templates. Django's default setup already includes it:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        ...
    }
]
```

With `APP_DIRS = True`, place your email templates inside any app's `templates/` directory and `Email()` will resolve them automatically.
If your project uses a custom `loaders` list instead of `APP_DIRS`, make sure `django.template.loaders.app_directories.Loader` is included.

_For more info on templates see [Template Convention](#template-convention) below._

No `migrate` step is needed unless you enable email logging (see [Email Logging](#email-logging) below).

---

## Usage

For each email, create three template files inside any app's `templates/` directory.
Templates can sit anywhere within the `templates/` directory:

```
your_app/
  templates/
    emails/
      welcome_email.subject   ← subject line (single line, no newlines)
      welcome_email.txt       ← plain-text body
      welcome_email.html      ← HTML body
```

Then send the email:

```python
from django_simple_mailer import Email

Email(
    template="emails/welcome_email",  # path relative to `templates/`
    context={"name": "Jane", "link": "https://app.example.com"},
    recipients=["jane@example.com"],
).send()
```

**`Email()` resolves templates using Django's template engine. `APP_DIRS = True` is the standard setup but any configured template discoverable by Django should work.**

---

## Error Handling

`send()` raises `MailerError` on delivery failure, you can get the original exception from `__cause__`:

```python
from django_simple_mailer import Email, MailerError

try:
    Email(template="welcome_email", context={...}, recipients=[...]).send()
except MailerError as exc:
    # The underlying SMTP/backend exception is available as exc.__cause__
    logger.error("Email delivery failed: %s", exc.__cause__)
```

---

## Email Logging

> **Disabled by default.** Enable with `SIMPLE_MAILER_LOG_EMAILS = True`.
> requires having a database configured and 'django.contrib.admin' installed.

When enabled, every `send()` call — success or failure — writes a `MailLog` record to the database. Logs are viewable and searchable from Django admin.

**Setup:**

```python
# settings.py
SIMPLE_MAILER_LOG_EMAILS = True  # default: False
```

Then run migrations to create the `MailLog` table:

```bash
python manage.py migrate
```

**What gets logged:**

| Field          | Description                          |
| -------------- | ------------------------------------ |
| `sent`         | `True` on success, `False` on error  |
| `error`        | Exception message if delivery failed |
| `sender`       | `DEFAULT_FROM_EMAIL` at send time    |
| `recipients`   | List of recipient addresses          |
| `subject`      | Rendered subject line                |
| `txt_message`  | Rendered plain-text body             |
| `html_message` | Rendered HTML body                   |

**Without a database:**

When `SIMPLE_MAILER_LOG_EMAILS = False` (the default), the library has zero database interaction and works in Django projects without a configured database.

---

## Settings Reference

| Setting                    | Default | Description                                                            |
| -------------------------- | ------- | ---------------------------------------------------------------------- |
| `SIMPLE_MAILER_LOG_EMAILS` | `False` | Persist send attempts to `MailLog`. Requires a database and `migrate`. |

---

## Template Convention

Each email requires exactly three files with the same name and path relative to any app's `templates/` directory:

| File             | Content                                                     |
| ---------------- | ----------------------------------------------------------- |
| `<name>.subject` | Subject line — rendered as a single line, newlines stripped |
| `<name>.txt`     | Plain-text email body                                       |
| `<name>.html`    | HTML email body                                             |

When using `Email()`, the `template` argument must match the path relative to `templates/`.
Subdirectories are supported — `template="emails/welcome/welcome_email"` resolves to `templates/emails/welcome/welcome_email.{subject,txt,html}`.

All three files are rendered with the same `context` dict passed to `Email()`.
