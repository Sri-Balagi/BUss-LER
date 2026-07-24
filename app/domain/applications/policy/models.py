
from pydantic import BaseModel, Field

from app.domain.intelligence.capability import CapabilityType


class ApplicationPolicy(BaseModel):
    """Defines the execution policy for an application."""
    app_id: str = Field(..., description="The application ID this policy applies to")
    allowed_capabilities: list[CapabilityType] = Field(default_factory=list)
    max_tokens_per_request: int | None = Field(None)
    max_execution_time_seconds: int | None = Field(None)
