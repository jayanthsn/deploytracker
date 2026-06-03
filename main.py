import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models.deployment  # noqa: F401 — register models with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(api_router)


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
