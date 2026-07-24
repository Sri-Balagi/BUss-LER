from typing import Any, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Structured error information."""
    code: str = Field(..., description="A machine-readable error code (e.g., 'not_found').")
    message: str = Field(..., description="A human-readable error description.")
    target: str | None = Field(default=None, description="The specific field or resource that caused the error.")
    details: list[Any] | None = Field(default=None, description="Additional context or validation errors.")


class BizOSResponse[DataT](BaseModel):
    """
    Standard envelope for all BizOS API responses.
    Ensures that every API endpoint returns a consistent JSON structure.
    """
    success: bool = Field(..., description="Indicates if the request was successful.")
    data: DataT | None = Field(default=None, description="The payload if successful.")
    error: ErrorDetail | None = Field(default=None, description="Error details if unsuccessful.")
    meta: dict[str, Any] = Field(default_factory=dict, description="Metadata like pagination, request IDs, or timestamps.")

    @classmethod
    def ok(cls, data: DataT, meta: dict[str, Any] | None = None) -> "BizOSResponse[DataT]":
        return cls(success=True, data=data, meta=meta or {})

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        target: str | None = None,
        details: list[Any] | None = None,
        meta: dict[str, Any] | None = None
    ) -> "BizOSResponse[None]":
        error = ErrorDetail(code=code, message=message, target=target, details=details)
        return cls(success=False, data=None, error=error, meta=meta or {})
