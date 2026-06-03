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
    """Payload for recording a new deployment event."""

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "service": "billing-api",
                "region": "us-east-1",
                "version": "2.1.0",
                "status": "inprogress",
                "deployed_at": "2025-04-28T14:32:00Z",
                "metadata": {
                    "commit_sha": "a1b2c3d",
                    "pipeline_id": "ci-789",
                    "triggered_by": "github-actions",
                },
            }
        },
    }

    service: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Service name — lowercase alphanumeric characters and hyphens only (e.g. `billing-api`).",
        examples=["billing-api", "auth-service", "notification-worker"],
    )
    region: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Cloud region where the deployment is targeted. Automatically normalised to lowercase.",
        examples=["us-east-1", "eu-west-1", "ap-southeast-1"],
    )
    version: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Version identifier for this release. Semver recommended.",
        examples=["2.1.0", "1.0.0-rc1", "20250428-abc123"],
    )
    status: DeploymentStatus = Field(
        DeploymentStatus.pending,
        description="Initial status of the deployment. Defaults to `pending` if omitted.",
    )
    deployed_at: datetime | None = Field(
        None,
        description="Deployment timestamp (UTC). Defaults to the current UTC time if omitted.",
        examples=["2025-04-28T14:32:00Z"],
    )
    metadata_: dict[str, Any] | None = Field(
        default=None,
        alias="metadata",
        description="Arbitrary key-value metadata — commit SHA, pipeline ID, triggered-by, etc.",
        examples=[{"commit_sha": "a1b2c3d", "pipeline_id": "ci-789"}],
    )

    @field_validator("region")
    @classmethod
    def region_lowercase(cls, v: str) -> str:
        return v.lower()


class DeploymentUpdate(BaseModel):
    """Partial update payload for an existing deployment."""

    model_config = {"populate_by_name": True}

    status: DeploymentStatus | None = Field(None, description="New status to set on the deployment.")
    version: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated version identifier.",
        examples=["2.1.1"],
    )
    metadata_: dict[str, Any] | None = Field(
        default=None,
        alias="metadata",
        description="Metadata to merge into the deployment record.",
    )


class DeploymentResponse(BaseModel):
    """Full deployment record returned by the API."""

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": 42,
                "service": "billing-api",
                "region": "us-east-1",
                "version": "2.1.0",
                "status": "success",
                "deployed_at": "2025-04-28T14:32:00Z",
                "metadata": {
                    "deployment_id": "deploy_042",
                    "duration_seconds": 245,
                    "commit_sha": "a1b2c3d",
                },
            }
        },
    }

    id: int = Field(..., description="Auto-assigned unique identifier for the deployment record.")
    service: str = Field(..., description="Name of the service that was deployed.")
    region: str = Field(..., description="Cloud region where the deployment ran.")
    version: str = Field(..., description="Version that was deployed.")
    status: DeploymentStatus = Field(..., description="Current status of the deployment.")
    deployed_at: datetime = Field(..., description="Timestamp when the deployment was recorded (UTC).")
    metadata_: dict[str, Any] | None = Field(
        default=None,
        serialization_alias="metadata",
        description="Arbitrary metadata attached to this deployment record.",
    )
