from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("/", response_model=list[DeploymentResponse])
async def list_deployments(
    region: str | None = Query(default=None),
    service: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Deployment)
    if region:
        stmt = stmt.where(Deployment.region == region.lower())
    if service:
        stmt = stmt.where(Deployment.service == service)
    if status:
        stmt = stmt.where(Deployment.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=DeploymentResponse, status_code=201)
async def create_deployment(
    payload: DeploymentCreate,
    db: AsyncSession = Depends(get_db),
):
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


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.patch("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: int,
    payload: DeploymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    for field, value in update_data.items():
        attr = "metadata_" if field == "metadata" else field
        setattr(deployment, attr, value.value if hasattr(value, "value") else value)

    await db.commit()
    await db.refresh(deployment)
    return deployment


@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).where(Deployment.id == deployment_id))
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    await db.delete(deployment)
    await db.commit()
