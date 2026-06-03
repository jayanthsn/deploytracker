import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

import app.models.deployment  # noqa: F401 — register models with Base
from app.api.v1 import v1_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.handler import error_response
from app.db.base import Base
from app.db.session import engine


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="DeployTracker API",
    version="0.1.0",
    description="""
Track every deployment across regions and services — with version, status, timestamp, and metadata.

## Response envelope

Every response is a JSON **object** — never a bare list or value.

| Scenario | Shape |
|---|---|
| Single item | `{"status": "success", "data": {...}}` |
| List | `{"status": "success", "data": [...], "count": N}` |
| Error | `{"status": "error", "code": "...", "message": "...", "timestamp": "...", "details": null}` |

## Deployment statuses

`pending` → `running` / `inprogress` → `success` | `failed` | `cancelled` | `rolled_back`

## Environments

| `APP_ENV` | Database |
|---|---|
| `development` | SQLite (`deploytracker.db`) |
| `testing` | SQLite (`deploytracker_test.db`) |
| `production` | PostgreSQL (via `DATABASE_URL`) |
""",
    openapi_tags=[
        {
            "name": "Deployments",
            "description": (
                "CRUD operations for deployment records. "
                "Each record captures a service name, region, version, status, timestamp, and optional metadata."
            ),
        },
        {
            "name": "System",
            "description": "Health and liveness endpoints.",
        },
    ],
    lifespan=lifespan,
)

app.include_router(v1_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(exc.code, exc.message, exc.status_code, exc.details)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("VALIDATION_ERROR", "Request validation failed.", 422, exc.errors())


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Returns the current liveness status and active environment. Use this to verify the service is up.",
    response_description="Service status and active environment name.",
)
async def health():
    return {"status": "ok", "env": settings.APP_ENV}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
    )
