from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.runtime.capabilities.permissions import CapabilityPermission


class CapabilityRequest(BaseModel):
    """
    Immutable value object defining exactly what is being asked of the system.
    """

    capability_id: str = Field(..., description="ID of the capability to execute.")
    operation: str = Field(..., description="Specific operation to perform.")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the operation."
    )
    execution_scope: str | None = Field(
        default=None, description="Scope of the execution (e.g., global, tenant)."
    )
    permissions: list[CapabilityPermission] = Field(
        default_factory=list, description="Permissions granted for this request."
    )
    timeout_ms: int | None = Field(
        default=None, description="Explicit timeout for this specific request."
    )
    trace_id: UUID | None = Field(default=None, description="Trace ID for observability.")
    caller_id: str | None = Field(
        default=None, description="Identity of the caller (e.g., agent ID)."
    )
    execution_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context for execution."
    )
    tenant_id: str | None = Field(default=None, description="Tenant ID for multi-tenant isolation.")
