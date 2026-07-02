# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for "Annuaire Contacts" — a Relationship Action Platform (RAP) managing contacts, relationship profiles, interactions, and follow-up actions. PostgreSQL via SQLAlchemy, Pydantic v2 schemas, Alembic migrations.

## Commands

```bash
# Local dev (no Docker)
python3 -m virtualenv --always-copy .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Docker (use "docker compose", not "docker-compose")
docker compose up -d          # postgres + backend
docker compose up -d postgres # db only, for local uvicorn against it

# Tests (require the API running against a real Postgres — see tests/README.md)
pytest tests/ -v
pytest tests/test_actions_integration.py -v
pytest tests/ -k "interaction" -v
pytest tests/ --cov=. --cov-report=html

# Version bump (writes VERSION file, optionally tags+pushes)
scripts/version_manager.sh show|major|minor|patch|set <x.y.z>|tag create

# Alembic migrations
alembic revision --autogenerate -m "message"
alembic upgrade head
```

Tests are integration tests, not unit tests with mocks: `test_relationship_profile_integration.py`, `test_interactions_integration.py`, `test_actions_integration.py`, `test_dashboard_integration.py` hit a live FastAPI server backed by a real PostgreSQL instance (via Docker Compose). Only `test_models.py` tests ORM/Pydantic models directly. `tests/conftest.py` just adds the repo root to `sys.path` so tests can `import main`, `models`, `database`.

## Architecture

`main.py` is a thin app factory: creates the `FastAPI` app, defines Swagger tag metadata, calls `init_db()` on startup, exposes `/health`, and delegates all endpoint registration to `routes.register_all_routes(app)`.

Routes are **not** `APIRouter`-based — each module in `routes/` defines a `register_<domain>_routes(app: FastAPI)` function that attaches `@app.get/post/...` decorators directly to the passed-in `app` instance. `routes/__init__.py` is the aggregation point calling each `register_*` function in sequence. When adding a new domain, follow this same pattern (new file + `register_*_routes` + wire it into `routes/__init__.py`), rather than switching to `APIRouter` unless asked.

Domain modules and their endpoints:
- `routes/contacts.py` — Contact CRUD + search (`/contacts`, `/contacts/search/{query}`)
- `routes/relationship_profiles.py` — one profile per contact (`/contacts/{id}/relationship-profile`)
- `routes/interactions.py` — interaction log per contact (`/contacts/{id}/interactions`)
- `routes/actions.py` — follow-up tasks/reminders (`/contacts/{id}/relationship-actions`, `/relationship-actions`, `/relationship-actions/due`, completion endpoint)
- `routes/dashboard.py` — `/rap/dashboard`, aggregated SQL metrics (due today, overdue, active relations, high potential, recent interactions)

`models.py` holds everything data-related in one file: SQLAlchemy ORM models (`ContactDB`, `RelationshipProfileDB`, `InteractionDB`, `RelationshipActionDB`) plus their `str, Enum` field types, plus the matching Pydantic `*Create` / `*Update` / `*Response` schemas. `ContactDB` cascades deletes to profiles/interactions/actions. `*Response` schemas serialize datetimes to ISO 8601 with a trailing `Z` via `field_serializer`; follow this convention for any new timestamp fields.

`database.py` — SQLAlchemy engine/session setup; `DATABASE_URL` env var (default points at the docker-compose Postgres); `get_db()` is the FastAPI dependency used across all routes.

Route handlers query `Session` directly (no repository/service layer) — business logic lives in the route function itself.
