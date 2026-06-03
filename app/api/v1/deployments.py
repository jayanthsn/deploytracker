from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.handler import HandledRoute
from app.db.session import get_db
from app.schemas.deployment import DeploymentCreate, DeploymentResponse
from app.schemas.response import DataEnvelope, ListEnvelope
from app.services import deployment as deployment_service

router = APIRouter(prefix="/deployments", tags=["deployments"], route_class=HandledRoute)


@router.get("/", response_model=ListEnvelope[DeploymentResponse])
async def list_deployments(
    region: str | None = Query(default=None),
    service: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items = await deployment_service.list_deployments(db, region, service, status)
    return {"status": "success", "data": items, "count": len(items)}


@router.post("/", response_model=DataEnvelope[DeploymentResponse], status_code=201)
async def create_deployment(payload: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    deployment = await deployment_service.create_deployment(db, payload)
    return {"status": "success", "data": deployment}


@router.get("/{deployment_id}", response_model=DataEnvelope[DeploymentResponse])
async def get_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    deployment = await deployment_service.get_deployment(db, deployment_id)
    return {"status": "success", "data": deployment}


@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    await deployment_service.delete_deployment(db, deployment_id)
