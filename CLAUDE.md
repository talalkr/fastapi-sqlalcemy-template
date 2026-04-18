# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
docker compose -f docker-compose.test.yml run --rm pytest

# Lint/format check
docker compose -f docker-compose.test.yml run --rm ruff

# Auto-fix lint/format
docker compose -f docker-compose.test.yml run --rm ruff_fix

# Type check (strict mypy)
docker compose -f docker-compose.test.yml run --rm mypy

# Run all pre-commit checks
pre-commit run --all-files

# Start app stack
docker compose up -d

# Create migration
MIGRATION_NAME="describe_change" docker compose run --rm create_app_migration
```

Local dev (requires local PostgreSQL):
```bash
poetry install
export $(cat vars/*.env | grep -v '^#' | xargs)
uvicorn app.main:app --reload --host 0.0.0.0
```

## Architecture

Layered: **routers → services → repositories → SQLAlchemy models**

- `app/routers/` — HTTP handlers, use `Depends()` for injection; all deps defined in `deps.py`
- `app/services/` — business logic, stateless
- `app/storage/db/repositories/` — data access via `BaseAsyncRepository[T, T_ID, T_CREATE, T_UPDATE]`
- `app/settings/` — Pydantic `BaseSettings` singletons (`env.py` for app, `db.py` for DB)

### Generic Repository

`BaseAsyncRepository` provides `get_all()`, `get_by_id()`, `insert()`, `update()`, `delete_by_id()`, `get_paginated()`, `get_count()`. Supports composite PKs via `pk_column` tuple. Raises `IntegrityException` / `NotFoundException` automatically.

Add new repo to `storage/db/repositories/__init__.py` (`all_repositories` list) for test isolation.

### Async

Everything is async — FastAPI lifespan, SQLAlchemy with `asyncpg`, all repository methods.

### Testing

- `tests/conftest.py` provides session-scoped `app`/`db_manager` fixtures and an `isolation` fixture that truncates all tables between tests
- Tests use `httpx.AsyncClient` with ASGI transport (no real HTTP)
- `pytest-asyncio` in `auto` mode — all async test functions collected automatically

### Migrations

Alembic auto-generates from model changes. Migrations run automatically at app startup. Always review auto-generated migrations before committing.

## Conventions

- **Strict mypy**: all functions need type annotations, no implicit `Any`
- **Line length**: 88 chars (Ruff)
- **First-party module**: `app`
- Pre-commit hooks run ruff → mypy → pytest in Docker; commit rejected on failure
- Env vars live in `vars/*.env` (checked into git, not secrets)
