# django-simple-mailer — task runner
# Usage: just <recipe>
# Requires: just (https://github.com/casey/just)

set dotenv-load  # automatically loads .env from the project root

# Run the full test suite
test:
    uv run pytest -x -ra -s --cache-clear --create-db --no-migrations --disable-warnings --showlocals -n4 tests

# Install dev dependencies
install:
    uv sync --group dev

# Build wheel + sdist into dist/
build:
    uv build

# Remove build artifacts
clean:
    rm -rf dist/

# Publish to PyPI
# Requires UV_PUBLISH_TOKEN env var:  UV_PUBLISH_TOKEN=pypi-... just publish
publish:
    uv publish

# Full release: clean → build → publish
release: clean build publish
