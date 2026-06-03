import os

# Must be set before any app module is imported so get_settings() picks up "testing"
os.environ["APP_ENV"] = "testing"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models.deployment  # noqa: F401 — register ORM models before create_all
from app.db.base import Base
from app.db.session import get_db
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./deploytracker_test.db"


@pytest_asyncio.fixture
async def client():
    """
    Spins up a fresh SQLite test DB for each test, overrides the get_db dependency
    so every request in the test uses the isolated test session, then tears it all down.
    """
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
