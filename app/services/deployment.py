import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DeploymentNotFound, InvalidDeploymentData
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate

# Service names must be lowercase alphanumeric with hyphens, no spaces or special chars
_SERVICE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _validate(payload: DeploymentCreate) -> None:
    if not _SERVICE_NAME_RE.match(payload.service):
        raise InvalidDeploymentData("service name must be lowercase alphanumeric with hyphens (e.g. 'my-service')")


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
    _validate(payload)
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
