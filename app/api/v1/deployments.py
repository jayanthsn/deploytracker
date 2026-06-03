from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.deployment import DeploymentCreate, DeploymentResponse
from app.services import deployment as deployment_service
from app.core.handler import HandledRoute

router = APIRouter(prefix="/deployments", tags=["deployments"], route_class=HandledRoute)


@router.get("/", response_model=list[DeploymentResponse])
async def list_deployments(
    region: str | None = Query(default=None),
    service: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await deployment_service.list_deployments(db, region, service, status)


@router.post("/", response_model=DeploymentResponse, status_code=201)
async def create_deployment(payload: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    return await deployment_service.create_deployment(db, payload)


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    return await deployment_service.get_deployment(db, deployment_id)


@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(deployment_id: int, db: AsyncSession = Depends(get_db)):
    await deployment_service.delete_deployment(db, deployment_id)
