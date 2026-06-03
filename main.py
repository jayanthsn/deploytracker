import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from app.api.v1 import v1_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.handler import error_response
from app.db.base import Base
from app.db.session import engine
import app.models.deployment  # noqa: F401 — register models with Base


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
    title="DeployTracker",
    description="Track deployments across regions with timestamps and metadata.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(v1_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(exc.code, exc.message, exc.status_code, exc.details)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response("VALIDATION_ERROR", "Request validation failed.", 422, exc.errors())


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
    )
