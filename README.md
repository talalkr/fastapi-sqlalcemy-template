# FastAPI 3T Template

A production-ready FastAPI template enforcing **Tests**, **Type-checking**, and **Tooling** via pre-commit hooks. Built with async PostgreSQL, strict mypy, Ruff, and full Docker support.

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Async web framework |
| PostgreSQL 18 + asyncpg | Database (fully async) |
| SQLAlchemy | ORM with async engine |
| Alembic | Database migrations |
| Pydantic | Data validation and settings |
| Poetry | Dependency management |
| Ruff | Linter and formatter |
| mypy (strict) | Static type checking |
| pytest + pytest-asyncio | Testing |
| Docker Compose | Containerized dev and test environments |
| pre-commit | Git hooks for CI checks |

## Prerequisites

- Python 3.14+
- [Poetry](https://python-poetry.org/docs/#installation) 2.1+
- Docker and Docker Compose
- [pre-commit](https://pre-commit.com/#install)

## Getting Started

### 1. Clone and install dependencies

```bash
git clone <repo-url> && cd fastapi-3T-template

poetry config --local virtualenvs.in-project true
poetry env use python3.14
poetry install
```

### 2. Install pre-commit hooks

```bash
pre-commit install
```

This registers the git hooks that run Ruff, mypy, and pytest **before every commit** using Docker.

### 3. Build and run

```bash
docker compose up -d
```

This starts:
- **app_db** -- PostgreSQL database
- **app_migrations** -- runs Alembic migrations automatically
- **app** -- FastAPI server at `http://localhost:8000`

API docs are available at `http://localhost:8000/docs`.

### Run without Docker

```bash
export $(cat vars/*.env | grep -v '^#' | xargs)
uvicorn app.main:app --reload --host 0.0.0.0
```

You need a running PostgreSQL instance matching the values in `vars/app.env`.

## Project Structure

```
app/
├── main.py                  # FastAPI app with lifespan events
├── logger.py                # Singleton logger
├── exceptions.py            # Custom exception classes
├── settings/
│   ├── env.py               # Environment settings (LOG_LEVEL, etc.)
│   └── db.py                # Database connection settings
├── routers/
│   ├── deps.py              # FastAPI dependency injection
│   └── infra.py             # Health check endpoints
├── services/
│   └── infra_service.py     # Business logic layer
└── storage/
    └── db/
        ├── base.py                    # SQLAlchemy declarative base
        ├── connection_manager.py      # Async DB engine management
        ├── repositories/
        │   └── base_async_repository.py  # Generic CRUD repository
        └── migrations/
            ├── alembic.ini
            ├── env.py
            └── versions/              # Migration files

tests/
├── conftest.py              # Fixtures (client, db, isolation)
├── test_routers/
└── test_services/

vars/
├── app.env                  # App environment variables
├── db.env                   # Database credentials
├── test.app.env             # Test app environment variables
└── test.db.env              # Test database credentials
```

## Development Workflow

### Pre-commit hooks

Every commit triggers these checks in order via Docker:

1. **Ruff format & fix** -- auto-formats and applies safe fixes
2. **Ruff check** -- lints for errors
3. **mypy** -- strict type checking
4. **pytest** -- runs the full test suite

If any check fails, the commit is rejected. Fix the issue and commit again.

### Running checks manually

```bash
# Lint and format check
docker compose -f docker-compose.test.yaml run --rm ruff

# Auto-fix formatting and lint issues
docker compose -f docker-compose.test.yaml run --rm ruff_fix

# Type checking
docker compose -f docker-compose.test.yaml run --rm mypy

# Tests
docker compose -f docker-compose.test.yaml run --rm pytest
```

### Run all pre-commit hooks without committing

```bash
pre-commit run --all-files
```

## Database Migrations

Migrations run automatically on `docker compose up`. To create a new migration after modifying models:

```bash
MIGRATION_NAME="describe_your_change" docker compose run --rm create_app_migration
```

This generates a new file in `app/storage/db/migrations/versions/`.

Always review auto-generated migrations before committing.

## Environment Variables

Environment files live in `vars/` and are **not** secret -- they contain local development defaults only.

| File | Used by |
|---|---|
| `vars/app.env` | App container |
| `vars/db.env` | PostgreSQL container |
| `vars/test.app.env` | Test runner |
| `vars/test.db.env` | Test database |

Key variables in `app.env`:

```
DB_HOST=app_db
DB_NAME=app_db
DB_USER=app_db
DB_PASSWORD=app_db
DB_PORT=5432
ENVIRONMENT=local
LOG_LEVEL=info
```

## Code Style

- **Line length**: 88 characters
- **Formatter**: Ruff (replaces Black)
- **Import sorting**: Ruff isort with `app` as first-party
- **Type checking**: mypy strict mode -- all functions must have type annotations, no implicit `Any`
- **Lint rules**: pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify, type-checking, ruff-specific

Configuration is in [pyproject.toml](pyproject.toml).

## Testing

Tests use `pytest-asyncio` with async mode set to `auto` -- all async test functions are collected automatically.

The test setup provides:
- A dedicated test PostgreSQL database (via `docker-compose.test.yaml`)
- Automatic migrations before test runs
- An async `httpx.AsyncClient` fixture for endpoint testing
- Data isolation between tests (automatic cleanup)

Add new test files under `tests/test_routers/` or `tests/test_services/`.

## VSCode Settings

The `.vscode/` directory is gitignored. To get consistent editor behavior across the team, create `.vscode/settings.json` with:

```json
{
    "python.analysis.autoImportCompletions": true,
    "python.terminal.activateEnvironment": true,
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.autoComplete.extraPaths": ["${workspaceFolder}"],
    "python.analysis.extraPaths": ["${workspaceFolder}"],
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.inlayHints.functionReturnTypes": true
}
```

These settings:
- Point the interpreter to the local Poetry virtualenv (`.venv/`)
- Enable auto-import completions
- Add the workspace root to the Python path for module resolution
- Enable basic type checking in the editor (strict checking is enforced by mypy in pre-commit)
- Show return type inlay hints for functions

## Adding a New Feature

1. Define your SQLAlchemy model in `app/storage/db/`
2. Create a repository extending `BaseAsyncRepository`
3. Add a service in `app/services/`
4. Add a router in `app/routers/` and register it in `app/main.py`
5. Wire dependencies in `app/routers/deps.py`
6. Generate a migration: `MIGRATION_NAME="add_feature" docker compose run --rm create_app_migration`
7. Write tests in `tests/`
8. Commit -- pre-commit hooks validate everything
