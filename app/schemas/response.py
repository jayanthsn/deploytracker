from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DataEnvelope(BaseModel, Generic[T]):
    """Success response wrapping a single object."""

    status: Literal["success"] = "success"
    data: T


class ListEnvelope(BaseModel, Generic[T]):
    """Success response wrapping a list of objects with a count."""

    status: Literal["success"] = "success"
    data: list[T]
    count: int
