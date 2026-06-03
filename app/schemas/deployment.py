from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DeploymentStatus(str, Enum):
    pending = "pending"
    running = "running"
    inprogress = "inprogress"
    success = "success"
    failed = "failed"
    cancelled = "cancelled"
    rolled_back = "rolled_back"


class DeploymentCreate(BaseModel):
    service: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=100)
    status: DeploymentStatus = DeploymentStatus.pending
    deployed_at: datetime | None = None
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata")

    model_config = {"populate_by_name": True}

    @field_validator("region")
    @classmethod
    def region_lowercase(cls, v: str) -> str:
        return v.lower()


class DeploymentUpdate(BaseModel):
    status: DeploymentStatus | None = None
    version: str | None = Field(default=None, min_length=1, max_length=100)
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata")

    model_config = {"populate_by_name": True}


class DeploymentResponse(BaseModel):
    id: int
    service: str
    region: str
    version: str
    status: DeploymentStatus
    deployed_at: datetime
    metadata_: dict[str, Any] | None = Field(default=None, serialization_alias="metadata")

    model_config = {"from_attributes": True, "populate_by_name": True}
