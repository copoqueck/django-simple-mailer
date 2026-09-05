# Development Guide

## Running tests

```bash
just test
```

---

## Testing in an external project locally

Install the library directly from the local path — no need to publish first:

```bash
# with uv
uv add /path/to/django-simple-mailer

# with pip
pip install /path/to/django-simple-mailer
```

Then in the project's `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_simple_mailer",
]
```

If email logging is needed, also add:

```python
SIMPLE_MAILER_LOG_EMAILS = True
```

And run migrations to create the `MailLog` table:

```bash
python manage.py migrate
```

---

## Publishing to PyPI

### 1. Set up your PyPI token

Generate an API token at <https://pypi.org/manage/account/token/>.

Add it to your local `.env` (see `.env.example`):

> For the very first publish, scope the token to your account. After the project
> exists on PyPI you can replace it with a project-scoped token.

### 2. Verify the package name is available

Search for `django-simple-mailer` on <https://pypi.org> before publishing.
If the name is taken, update `name` in `pyproject.toml` and rebuild.

### 3. Release

```bash
just release
```

This runs `clean` → `build` → `publish` in one step. The token is read
automatically from `.env` — no need to pass it explicitly.

To run steps individually:

```bash
just build    # produces dist/*.whl and dist/*.tar.gz
just publish  # uploads to PyPI
```
