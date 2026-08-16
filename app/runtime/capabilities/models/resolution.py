from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.runtime.capabilities.models.specification import CapabilitySpecification


class CapabilityResolutionContext(BaseModel):
    capability_id: str
    operation: str
    requested_version: str | None = None
    execution_scope: str | None = None
    permissions: list[str] = Field(default_factory=list)
    caller_agent_id: str | None = None
    caller_capability: str | None = None
    execution_trace_id: UUID | None = None
    execution_budget: dict[str, Any] | None = None
    priority: int = 0
    tenant_id: str | None = None
    policy_overrides: dict[str, Any] = Field(default_factory=dict)


class CapabilityResolutionDecision(BaseModel):
    selected_factory: Any  # ICapabilityFactory
    selected_specification: CapabilitySpecification
    compatibility_score: float = 1.0
    version_resolution: str
    fallback_candidates: list[str] = Field(default_factory=list)
    resolution_trace: list[str] = Field(default_factory=list)
    selection_reason: str = ""

    class Config:
        arbitrary_types_allowed = True
