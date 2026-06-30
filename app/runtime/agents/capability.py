from pydantic import BaseModel, Field

from app.runtime.agents.permissions import AgentPermission


class Capability(BaseModel):
    """
    Structured value object for an agent capability.
    Enables rich semantic matching by the Registry.
    """
    capability_id: str = Field(description="Unique identifier for the capability (e.g., 'revenue-forecaster')")
    version: str = Field(default="1.0.0", description="Semantic version of this capability")
    category: str = Field(default="general", description="Category for grouping capabilities")
    required_permissions: list[AgentPermission] = Field(default_factory=list, description="Permissions required to execute this capability")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional context or constraints")

    def __hash__(self):
        return hash((self.capability_id, self.version))

    def __eq__(self, other):
        if not isinstance(other, Capability):
            return False
        return self.capability_id == other.capability_id and self.version == other.version
