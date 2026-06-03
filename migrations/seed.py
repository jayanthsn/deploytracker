"""
Seed script — loads 32 mock deployments into the database.

Defaults to development (SQLite). Override with APP_ENV env var.

Usage:
    uv run python migrations/seed.py               # development (default)
    APP_ENV=production uv run python migrations/seed.py
    uv run python migrations/seed.py --force       # re-seed even if data exists
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

# Allow running directly from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("APP_ENV", "development")

from sqlalchemy import func, select  # noqa: E402

import app.models.deployment  # noqa: F401 — register ORM model before create_all
from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import AsyncSessionLocal, engine  # noqa: E402
from app.models.deployment import Deployment  # noqa: E402

# fmt: off
MOCK_DEPLOYMENTS = [
    # ── billing-api ──────────────────────────────────────────────────────────
    {"id": "deploy_001", "service": "billing-api",          "region": "us-east-1",      "version": "1.0.0", "status": "success",    "duration": 182, "timestamp": "2025-01-10T08:15:00Z", "commit_sha": "a1b2c3d"},
    {"id": "deploy_002", "service": "billing-api",          "region": "us-east-1",      "version": "1.0.1", "status": "failed",     "duration": 47,  "timestamp": "2025-01-25T14:32:00Z", "commit_sha": "e4f5a6b"},
    {"id": "deploy_003", "service": "billing-api",          "region": "us-west-2",      "version": "1.0.1", "status": "success",    "duration": 201, "timestamp": "2025-01-25T16:10:00Z", "commit_sha": "e4f5a6b"},
    {"id": "deploy_004", "service": "billing-api",          "region": "eu-west-1",      "version": "1.1.0", "status": "success",    "duration": 265, "timestamp": "2025-02-14T09:00:00Z", "commit_sha": "c7d8e9f"},
    {"id": "deploy_005", "service": "billing-api",          "region": "us-east-1",      "version": "1.1.1", "status": "cancelled",  "duration": 12,  "timestamp": "2025-03-02T11:45:00Z", "commit_sha": "f0a1b2c"},
    {"id": "deploy_006", "service": "billing-api",          "region": "us-east-1",      "version": "1.2.0", "status": "success",    "duration": 310, "timestamp": "2025-03-20T10:20:00Z", "commit_sha": "3d4e5f6"},
    {"id": "deploy_007", "service": "billing-api",          "region": "ap-southeast-1", "version": "1.2.1", "status": "failed",     "duration": 88,  "timestamp": "2025-04-05T07:30:00Z", "commit_sha": "7a8b9c0"},
    {"id": "deploy_008", "service": "billing-api",          "region": "us-east-1",      "version": "2.0.0", "status": "inprogress", "duration": 0,   "timestamp": "2025-04-28T14:32:00Z", "commit_sha": "d1e2f3a"},

    # ── auth-service ─────────────────────────────────────────────────────────
    {"id": "deploy_009", "service": "auth-service",         "region": "us-east-1",      "version": "3.0.0", "status": "success",    "duration": 140, "timestamp": "2025-01-15T09:45:00Z", "commit_sha": "b4c5d6e"},
    {"id": "deploy_010", "service": "auth-service",         "region": "us-west-2",      "version": "3.0.1", "status": "success",    "duration": 155, "timestamp": "2025-02-01T13:00:00Z", "commit_sha": "f7a8b9c"},
    {"id": "deploy_011", "service": "auth-service",         "region": "eu-west-1",      "version": "3.1.0", "status": "failed",     "duration": 320, "timestamp": "2025-02-18T15:20:00Z", "commit_sha": "0d1e2f3"},
    {"id": "deploy_012", "service": "auth-service",         "region": "eu-west-1",      "version": "3.1.0", "status": "success",    "duration": 298, "timestamp": "2025-02-19T09:05:00Z", "commit_sha": "0d1e2f3"},
    {"id": "deploy_013", "service": "auth-service",         "region": "us-east-1",      "version": "3.2.0", "status": "cancelled",  "duration": 5,   "timestamp": "2025-03-10T16:00:00Z", "commit_sha": "4a5b6c7"},
    {"id": "deploy_014", "service": "auth-service",         "region": "us-west-2",      "version": "3.2.0", "status": "success",    "duration": 173, "timestamp": "2025-03-10T17:30:00Z", "commit_sha": "4a5b6c7"},
    {"id": "deploy_015", "service": "auth-service",         "region": "ap-southeast-1", "version": "3.3.0", "status": "inprogress", "duration": 0,   "timestamp": "2025-04-12T06:15:00Z", "commit_sha": "8d9e0f1"},
    {"id": "deploy_016", "service": "auth-service",         "region": "us-east-1",      "version": "4.0.0", "status": "failed",     "duration": 512, "timestamp": "2025-05-05T11:10:00Z", "commit_sha": "2a3b4c5"},

    # ── notification-worker ───────────────────────────────────────────────────
    {"id": "deploy_017", "service": "notification-worker",  "region": "us-east-1",      "version": "0.9.0", "status": "success",    "duration": 95,  "timestamp": "2025-01-08T07:00:00Z", "commit_sha": "6d7e8f9"},
    {"id": "deploy_018", "service": "notification-worker",  "region": "us-east-1",      "version": "0.9.1", "status": "success",    "duration": 102, "timestamp": "2025-01-22T10:30:00Z", "commit_sha": "a0b1c2d"},
    {"id": "deploy_019", "service": "notification-worker",  "region": "eu-west-1",      "version": "1.0.0", "status": "failed",     "duration": 430, "timestamp": "2025-02-10T14:00:00Z", "commit_sha": "3e4f5a6"},
    {"id": "deploy_020", "service": "notification-worker",  "region": "eu-west-1",      "version": "1.0.0", "status": "success",    "duration": 388, "timestamp": "2025-02-11T09:20:00Z", "commit_sha": "3e4f5a6"},
    {"id": "deploy_021", "service": "notification-worker",  "region": "us-west-2",      "version": "1.0.1", "status": "cancelled",  "duration": 8,   "timestamp": "2025-03-15T15:45:00Z", "commit_sha": "b7c8d9e"},
    {"id": "deploy_022", "service": "notification-worker",  "region": "us-east-1",      "version": "1.1.0", "status": "success",    "duration": 210, "timestamp": "2025-04-01T08:00:00Z", "commit_sha": "0f1a2b3"},
    {"id": "deploy_023", "service": "notification-worker",  "region": "ap-southeast-1", "version": "1.1.0", "status": "success",    "duration": 225, "timestamp": "2025-04-01T10:00:00Z", "commit_sha": "0f1a2b3"},
    {"id": "deploy_024", "service": "notification-worker",  "region": "us-east-1",      "version": "1.2.0", "status": "inprogress", "duration": 0,   "timestamp": "2025-05-20T12:30:00Z", "commit_sha": "4c5d6e7"},

    # ── user-service ──────────────────────────────────────────────────────────
    {"id": "deploy_025", "service": "user-service",         "region": "us-east-1",      "version": "2.1.0", "status": "success",    "duration": 175, "timestamp": "2025-01-12T09:00:00Z", "commit_sha": "f8a9b0c"},
    {"id": "deploy_026", "service": "user-service",         "region": "us-west-2",      "version": "2.1.1", "status": "failed",     "duration": 560, "timestamp": "2025-01-30T13:15:00Z", "commit_sha": "1d2e3f4"},
    {"id": "deploy_027", "service": "user-service",         "region": "us-west-2",      "version": "2.1.1", "status": "success",    "duration": 490, "timestamp": "2025-01-31T08:45:00Z", "commit_sha": "1d2e3f4"},
    {"id": "deploy_028", "service": "user-service",         "region": "eu-west-1",      "version": "2.2.0", "status": "success",    "duration": 220, "timestamp": "2025-02-25T11:30:00Z", "commit_sha": "5a6b7c8"},
    {"id": "deploy_029", "service": "user-service",         "region": "us-east-1",      "version": "2.2.1", "status": "cancelled",  "duration": 3,   "timestamp": "2025-03-18T16:50:00Z", "commit_sha": "9d0e1f2"},
    {"id": "deploy_030", "service": "user-service",         "region": "ap-southeast-1", "version": "2.3.0", "status": "success",    "duration": 305, "timestamp": "2025-04-15T05:30:00Z", "commit_sha": "3a4b5c6"},
    {"id": "deploy_031", "service": "user-service",         "region": "us-east-1",      "version": "2.3.1", "status": "failed",     "duration": 74,  "timestamp": "2025-05-10T10:00:00Z", "commit_sha": "7d8e9f0"},
    {"id": "deploy_032", "service": "user-service",         "region": "us-east-1",      "version": "2.4.0", "status": "inprogress", "duration": 0,   "timestamp": "2025-06-01T08:00:00Z", "commit_sha": "a1b2c3e"},
]
# fmt: on


async def run(*, force: bool = False) -> None:
    print(f"[seed] env={settings.APP_ENV}  db={settings.async_database_url}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        count = (await session.execute(select(func.count()).select_from(Deployment))).scalar_one()

        if count > 0 and not force:
            print(f"[seed] {count} record(s) already exist. Use --force to re-seed.")
            return

        if count > 0:
            print(f"[seed] --force: deleting {count} existing record(s).")
            for dep in (await session.execute(select(Deployment))).scalars().all():
                await session.delete(dep)
            await session.commit()

        deployments = [
            Deployment(
                service=d["service"],
                region=d["region"],
                version=d["version"],
                status=d["status"],
                deployed_at=datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")),
                metadata_={
                    "deployment_id": d["id"],
                    "duration_seconds": d["duration"],
                    "commit_sha": d["commit_sha"],
                },
            )
            for d in MOCK_DEPLOYMENTS
        ]
        session.add_all(deployments)
        await session.commit()

    print(f"[seed] Inserted {len(MOCK_DEPLOYMENTS)} deployments.")
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the deploytracker database with mock data.")
    parser.add_argument("--force", action="store_true", help="Delete existing records and re-seed.")
    args = parser.parse_args()
    asyncio.run(run(force=args.force))
