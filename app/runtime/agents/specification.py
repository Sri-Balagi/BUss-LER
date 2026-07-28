from enum import Enum

from pydantic import BaseModel, Field

from app.runtime.agents.permissions import AgentPermission


class ExecutionType(str, Enum):
    """Supported execution models for an agent."""

    SYNCHRONOUS = "SYNCHRONOUS"
    ASYNCHRONOUS = "ASYNCHRONOUS"


class AgentSpecification(BaseModel):
    """
    Defines the static runtime identity and capabilities of an agent.
    Used by the Registry for capability mapping and routing.
    """

    identity: str = Field(
        description="Unique identity slug for the agent class (e.g., 'revenue-forecaster')"
    )
    capabilities: list[str] = Field(
        default_factory=list, description="List of capabilities this agent fulfills"
    )
    permissions: list[AgentPermission] = Field(
        default_factory=list, description="Declarative boundaries enforced by the Context"
    )
    execution_support: ExecutionType = Field(default=ExecutionType.ASYNCHRONOUS)
    description: str = Field(default="", description="Human-readable description of capabilities")
