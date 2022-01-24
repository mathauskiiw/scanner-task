#!/bin/sh

# mypy checks, ignoring missing stubs warnings
poetry run mypy . --ignore-missing-imports

# run the application
poetry run python -m scanner_task --headless