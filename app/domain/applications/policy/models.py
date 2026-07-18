from pydantic import BaseModel, Field
from typing import List, Optional

from app.domain.intelligence.capability import CapabilityType

class ApplicationPolicy(BaseModel):
    """Defines the execution policy for an application."""
    app_id: str = Field(..., description="The application ID this policy applies to")
    allowed_capabilities: List[CapabilityType] = Field(default_factory=list)
    max_tokens_per_request: Optional[int] = Field(None)
    max_execution_time_seconds: Optional[int] = Field(None)
