#!/bin/bash

set -eu -o pipefail

export DATABASE_URL=sqlite://:memory:

BLUE="\e[34m"
NC="\e[0m"

# Run Python formatter (ruff) -- but let Django migrations get a pass.
printf "${BLUE}Running ruff format...${NC}\n"
ruff format --check server

# Run Python linter (ruff).
printf "${BLUE}Running ruff...${NC}\n"
ruff check server

# Run the Python type checker (mypy).
printf "${BLUE}Running mypy...${NC}\n"
mypy server

# Run Python tests
printf "${BLUE}Running tests...${NC}\n"
CELERY_TASK_ALWAYS_EAGER=true python manage.py test
