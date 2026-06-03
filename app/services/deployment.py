from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate
from app.core.exceptions import DeploymentNotFound


async def list_deployments(
    db: AsyncSession,
    region: str | None = None,
    service: str | None = None,
    status: str | None = None,
) -> list[Deployment]:
    stmt = select(Deployment)
    if region:
        stmt = stmt.where(Deployment.region == region.lower())
    if service:
        stmt = stmt.where(Deployment.service == service)
    if status:
        stmt = stmt.where(Deployment.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_deployment(db: AsyncSession, payload: DeploymentCreate) -> Deployment:
    deployment = Deployment(
        service=payload.service,
        region=payload.region,
        version=payload.version,
        status=payload.status.value,
        deployed_at=payload.deployed_at or datetime.now(timezone.utc),
        metadata_=payload.metadata_,
    )
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return deployment


async def get_deployment(db: AsyncSession, deployment_id: int) -> Deployment:
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise DeploymentNotFound()
    return deployment


async def delete_deployment(db: AsyncSession, deployment_id: int) -> None:
    deployment = await get_deployment(db, deployment_id)
    await db.delete(deployment)
    await db.commit()
