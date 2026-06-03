from fastapi import APIRouter
from app.api.v1.deployments import router as deployments_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(deployments_router)
