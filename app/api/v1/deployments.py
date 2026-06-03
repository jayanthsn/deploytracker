from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.handler import HandledRoute
from app.db.session import get_db
from app.schemas.deployment import DeploymentCreate, DeploymentResponse
from app.schemas.response import DataEnvelope, ErrorResponse, ListEnvelope
from app.services import deployment as deployment_service

router = APIRouter(prefix="/deployments", tags=["Deployments"], route_class=HandledRoute)

_ERRORS = {
    422: {"model": ErrorResponse, "description": "Request validation failed."},
    500: {"model": ErrorResponse, "description": "Unexpected server error."},
}

_ERRORS_WITH_404 = {
    **_ERRORS,
    404: {"model": ErrorResponse, "description": "Deployment record not found."},
}


@router.get(
    "/",
    response_model=ListEnvelope[DeploymentResponse],
    summary="List deployments",
    description=(
        "Return all recorded deployments, optionally narrowed by **region**, **service**, "
        "or **status**. Results are unordered — apply filters to reduce the result set."
    ),
    response_description="Paginated list of deployment records wrapped in the standard envelope.",
    responses=_ERRORS,
)
async def list_deployments(
    region: str | None = Query(
        default=None,
        description="Filter by cloud region (exact match, case-insensitive). Example: `us-east-1`.",
        examples=["us-east-1", "eu-west-1", "ap-southeast-1"],
    ),
    service: str | None = Query(
        default=None,
        description="Filter by service name (exact match). Example: `billing-api`.",
        examples=["billing-api", "auth-service", "notification-worker"],
    ),
    status: str | None = Query(
        default=None,
        description=(
            "Filter by deployment status. "
            "Accepted values: `pending`, `running`, `inprogress`, `success`, `failed`, `cancelled`, `rolled_back`."
        ),
        examples=["success", "failed", "inprogress"],
    ),
    db: AsyncSession = Depends(get_db),
):
    items = await deployment_service.list_deployments(db, region, service, status)
    return {"status": "success", "data": items, "count": len(items)}


@router.post(
    "/",
    response_model=DataEnvelope[DeploymentResponse],
    status_code=201,
    summary="Record a deployment",
    description=(
        "Create a new deployment record. "
        "The `service` name must be **lowercase alphanumeric with hyphens** (e.g. `billing-api`). "
        "Region is normalised to lowercase automatically. "
        "`deployed_at` defaults to the current UTC time if omitted."
    ),
    response_description="The newly created deployment record.",
    responses={
        201: {"description": "Deployment successfully recorded."},
        **_ERRORS,
    },
)
async def create_deployment(payload: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    deployment = await deployment_service.create_deployment(db, payload)
    return {"status": "success", "data": deployment}


@router.get(
    "/{deployment_id}",
    response_model=DataEnvelope[DeploymentResponse],
    summary="Get a deployment",
    description="Fetch a single deployment record by its numeric ID.",
    response_description="The deployment record matching the given ID.",
    responses=_ERRORS_WITH_404,
)
async def get_deployment(
    deployment_id: int = Path(
        ...,
        description="Numeric ID of the deployment record to retrieve.",
        examples=[42],
        ge=1,
    ),
    db: AsyncSession = Depends(get_db),
):
    deployment = await deployment_service.get_deployment(db, deployment_id)
    return {"status": "success", "data": deployment}


@router.delete(
    "/{deployment_id}",
    status_code=204,
    summary="Delete a deployment",
    description="Permanently remove a deployment record. This action cannot be undone.",
    response_description="No content — the record has been deleted.",
    responses={
        **_ERRORS_WITH_404,
        204: {"description": "Deployment successfully deleted."},
    },
)
async def delete_deployment(
    deployment_id: int = Path(
        ...,
        description="Numeric ID of the deployment record to delete.",
        examples=[42],
        ge=1,
    ),
    db: AsyncSession = Depends(get_db),
):
    await deployment_service.delete_deployment(db, deployment_id)
