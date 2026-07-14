from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Structured error information."""
    code: str = Field(..., description="A machine-readable error code (e.g., 'not_found').")
    message: str = Field(..., description="A human-readable error description.")
    target: Optional[str] = Field(default=None, description="The specific field or resource that caused the error.")
    details: Optional[List[Any]] = Field(default=None, description="Additional context or validation errors.")


class BizOSResponse(BaseModel, Generic[DataT]):
    """
    Standard envelope for all BizOS API responses.
    Ensures that every API endpoint returns a consistent JSON structure.
    """
    success: bool = Field(..., description="Indicates if the request was successful.")
    data: Optional[DataT] = Field(default=None, description="The payload if successful.")
    error: Optional[ErrorDetail] = Field(default=None, description="Error details if unsuccessful.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata like pagination, request IDs, or timestamps.")

    @classmethod
    def ok(cls, data: DataT, meta: Optional[Dict[str, Any]] = None) -> "BizOSResponse[DataT]":
        return cls(success=True, data=data, meta=meta or {})

    @classmethod
    def fail(
        cls, 
        code: str, 
        message: str, 
        target: Optional[str] = None, 
        details: Optional[List[Any]] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> "BizOSResponse[None]":
        error = ErrorDetail(code=code, message=message, target=target, details=details)
        return cls(success=False, data=None, error=error, meta=meta or {})
