from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class DataEnvelope(BaseModel, Generic[T]):
    """Success response wrapping a single object."""

    status: Literal["success"] = Field("success", description="Always 'success' for non-error responses.")
    data: T = Field(..., description="The response payload.")


class ListEnvelope(BaseModel, Generic[T]):
    """Success response wrapping a list of objects with a count."""

    status: Literal["success"] = Field("success", description="Always 'success' for non-error responses.")
    data: list[T] = Field(..., description="List of result items.")
    count: int = Field(..., description="Total number of items returned in this response.", examples=[3])


class ErrorResponse(BaseModel):
    """Standard error envelope returned for all 4xx and 5xx responses."""

    status: Literal["error"] = Field("error", description="Always 'error' for error responses.")
    code: str = Field(..., description="Machine-readable error code.", examples=["DEPLOYMENT_NOT_FOUND"])
    message: str = Field(..., description="Human-readable description of the error.")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of when the error occurred.")
    details: Any = Field(None, description="Optional extra detail (e.g. validation field errors).")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "code": "DEPLOYMENT_NOT_FOUND",
                "message": "The requested deployment does not exist.",
                "timestamp": "2025-04-28T14:32:00Z",
                "details": None,
            }
        }
    }
