# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                        # install all dependencies
uv run python main.py          # start dev server (auto-reload on)
uv run uvicorn main:app --reload

uv add <package>               # add a runtime dependency
uv add --dev <package>         # add a dev dependency
```

Docs at `http://localhost:8000/docs` once running.

## Architecture

Three strict layers — never skip one:

1. **Routes / Views** (`app/api/v1/deployments.py`) — URL bindings and thin view functions. Views only call service functions; zero business logic here.
2. **Services** (`app/services/`) — all business logic and DB queries. Raise `AppException` subclasses (never `HTTPException`) on domain errors.
3. **Models / Schemas** (`app/models/`, `app/schemas/`) — SQLAlchemy ORM models and Pydantic v2 request/response schemas.

Supporting pieces:
- `app/core/config.py` — `Settings` (pydantic-settings, loaded from `.env`). Import `settings` singleton.
- `app/core/exceptions.py` — `AppException` base class; add new domain exceptions here.
- `app/core/handler.py` — `HandledRoute` (custom `APIRoute` subclass) applied via `route_class=HandledRoute` on every router. Catches `AppException` → structured JSON error, `RequestValidationError` → 422, anything else → 500 + full traceback logged at DEBUG.
- `app/api/v1/router.py` — single place where all v1 sub-routers are registered onto `v1_router`.
- `main.py` — FastAPI app, lifespan (table auto-creation), global exception handlers, logging setup.

## Error response shape

All errors — including validation and unhandled — return this structure:

```json
{
  "status": "error",
  "code": "DEPLOYMENT_NOT_FOUND",
  "message": "The requested deployment does not exist.",
  "timestamp": "2026-06-03T09:33:28Z",
  "details": null
}
```

## Environment

| Variable       | dev default            | prod value                |
|----------------|------------------------|---------------------------|
| `APP_ENV`      | `development`          | `production`              |
| `LOG_LEVEL`    | `DEBUG`                | `INFO`                    |
| `DB_PATH`      | `./deploytracker.db`   | *(ignored)*               |
| `DATABASE_URL` | *(ignored)*            | postgres+asyncpg DSN      |

Copy `.env.example` → `.env` to get started. `APP_ENV=development` uses SQLite; `production` switches to PostgreSQL automatically — no code change needed.

## Adding a new endpoint

1. Add the domain exception to `app/core/exceptions.py` if needed.
2. Add the business logic function to the relevant `app/services/` file.
3. Add the route + view to the relevant `app/api/v1/<resource>.py` (router must use `route_class=HandledRoute`).
4. If it's a new resource, create the service/route files and register the router in `app/api/v1/router.py`.
