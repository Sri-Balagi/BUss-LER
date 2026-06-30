from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.runtime.capabilities.permissions import CapabilityPermission
from app.runtime.capabilities.policies import CapabilityPolicy


class CapabilitySpecification(BaseModel):
    """
    Runtime identity and definition for a capability.
    """
    capability_id: str = Field(..., description="Unique identifier for the capability.")
    name: str = Field(..., description="Human-readable name.")
    category: str = Field(..., description="Category for grouping (e.g., Network, Database).")
    version: str = Field(default="1.0.0", description="Semantic version of the capability.")
    supported_operations: list[str] = Field(default_factory=list, description="Operations this capability can perform.")
    permissions_required: list[CapabilityPermission] = Field(default_factory=list, description="Permissions required to execute.")
    execution_mode: str = Field(default="async", description="Execution mode (async, thread, process).")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata.")
    policy: CapabilityPolicy = Field(default_factory=CapabilityPolicy, description="Execution constraints.")
