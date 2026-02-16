set shell := ["bash", "-c"]

default:
    @just --list

# Initializes the project (uv-based)
setup:
    uv venv
    uv sync --extra dev
    cp -n .env.example .env || true

# Runs bootstrap steps locally
dev:
    bash scripts/bootstrap.sh all

# Bootstrap shortcuts (single source of truth: scripts/bootstrap.sh)
bootstrap:
    bash scripts/bootstrap.sh all

bootstrap-load-env:
    bash scripts/bootstrap.sh load_env

bootstrap-prepare-dirs:
    bash scripts/bootstrap.sh prepare_dirs

bootstrap-test:
    bash scripts/bootstrap.sh run_tests

bootstrap-info:
    bash scripts/bootstrap.sh show_info

# Formats code (Ruff)
format:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Checks code quality (read-only)
lint:
    uv run ruff check src tests
    uv run ruff format --check src tests
    uv run --with black black --check src tests
    uv run --with flake8 flake8 src tests

# Type checking
typecheck:
    uv run mypy src

# Runs tests
test:
    uv run pytest

# Builds distributions
build:
    uv run --with build python -m build

# Complete quality check (CI simulation)
check: lint typecheck test

# Full local CI (includes build)
ci: lint typecheck test build

# Starts Docker container (deployment testing)
docker-up:
    docker-compose up -d --build
    docker-compose logs -f

# Stops Docker container
docker-down:
    docker-compose down

# Cleans artifacts
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    rm -rf .pytest_cache .coverage htmlcov .ruff_cache build dist
