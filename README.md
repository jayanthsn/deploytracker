# DeployTracker

A deployment tracking service built with **FastAPI** and **SQLAlchemy**. Records every deployment across regions — capturing the service name, region, version, status, timestamp, and arbitrary metadata — and exposes a REST API to query and manage that history.

## Features

- Track deployments across multiple regions and services
- Store version, status, timestamp, and freeform metadata per deployment
- Filter deployments by region, service, or status
- SQLite in development, PostgreSQL in production (switched via `APP_ENV`)
- Fully async stack (FastAPI + SQLAlchemy async + aiosqlite / asyncpg)
- Pydantic v2 request/response validation

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
# Install dependencies
uv sync

# Copy and edit environment config
cp .env.example .env
```

## Running

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn main:app --reload
```

## API Documentation

Once the server is running, interactive docs are available at:

| UI        | URL                               | Description                              |
|-----------|-----------------------------------|------------------------------------------|
| Swagger   | `http://localhost:8000/docs`      | Interactive API explorer (Swagger UI)    |
| ReDoc     | `http://localhost:8000/redoc`     | Alternate read-only reference docs       |
| OpenAPI   | `http://localhost:8000/openapi.json` | Raw OpenAPI schema (JSON)             |

## Environment Variables

| Variable       | Default                                                | Description                                         |
|----------------|--------------------------------------------------------|-----------------------------------------------------|
| `APP_ENV`      | `development`                                          | `development` → SQLite; `production` → PostgreSQL   |
| `HOST`         | `0.0.0.0`                                              | Bind address for the server                         |
| `PORT`         | `8000`                                                 | Port for the server                                 |
| `DB_PATH`      | `./deploytracker.db`                                   | SQLite database file path (development only)        |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@.../deploytracker` | PostgreSQL DSN (production only)                    |

## Project Structure

```
deploytracker/
├── app/
│   ├── api/v1/
│   │   └── deployments.py   # CRUD endpoints
│   ├── core/
│   │   └── config.py        # Pydantic settings loaded from .env
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   └── session.py       # Async engine + session factory
│   ├── models/
│   │   └── deployment.py    # ORM model
│   └── schemas/
│       └── deployment.py    # Pydantic request/response schemas
├── main.py                  # FastAPI app + lifespan (table creation)
├── .env                     # Local config (git-ignored)
├── .env.example             # Config template (committed)
└── pyproject.toml
```

## Migrations

Seed the database with 32 mock deployments across 4 services (`billing-api`, `auth-service`, `notification-worker`, `user-service`):

```bash
# Development (default) — writes to deploytracker.db
uv run python migrations/seed.py

# Re-seed (wipes existing records first)
uv run python migrations/seed.py --force

# Production — uses DATABASE_URL from .env
APP_ENV=production uv run python migrations/seed.py
```

Each seeded record includes a `metadata` payload with `deployment_id`, `duration_seconds`, and `commit_sha`.

## API Endpoints

| Method   | Path                        | Description                        |
|----------|-----------------------------|------------------------------------|
| `GET`    | `/api/v1/deployments/`      | List deployments (filterable)      |
| `POST`   | `/api/v1/deployments/`      | Record a new deployment            |
| `GET`    | `/api/v1/deployments/{id}`  | Get a single deployment            |
| `DELETE` | `/api/v1/deployments/{id}`  | Remove a deployment record         |
| `GET`    | `/health`                   | Health check                       |
