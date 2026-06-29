from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from app.runtime.capabilities.models.specification import CapabilitySpecification

class CapabilityResolutionContext(BaseModel):
    capability_id: str
    operation: str
    requested_version: Optional[str] = None
    execution_scope: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    caller_agent_id: Optional[str] = None
    caller_capability: Optional[str] = None
    execution_trace_id: Optional[UUID] = None
    execution_budget: Optional[Dict[str, Any]] = None
    priority: int = 0
    tenant_id: Optional[str] = None
    policy_overrides: Dict[str, Any] = Field(default_factory=dict)

class CapabilityResolutionDecision(BaseModel):
    selected_factory: Any # ICapabilityFactory
    selected_specification: CapabilitySpecification
    compatibility_score: float = 1.0
    version_resolution: str
    fallback_candidates: List[str] = Field(default_factory=list)
    resolution_trace: List[str] = Field(default_factory=list)
    selection_reason: str = ""
    
    class Config:
        arbitrary_types_allowed = True
