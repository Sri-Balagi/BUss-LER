import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.runtime.agents.capability import Capability
from app.shared.enums import AgentStatus, AgentType, AgentCapability, MemoryScope

class AgentTemplate(BaseModel):
    """
    Template for creating specialized agents (e.g. Sales Agent, Planner).
    Belongs to a module or is globally registered.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str
    description: str
    capabilities: list[Any] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    reasoning_provider: str | None = None
    default_system_prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class Agent(BaseModel):
    """
    First-class Agent Domain model.
    Represents an AI actor runtime instance registered within BizOS.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str | None = None
    name: str
    description: str
    agent_type: AgentType | None = None
    version: str = "1.0.0"
    status: AgentStatus = AgentStatus.REGISTERED
    capabilities: list[Any] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)
    memory_references: dict[MemoryScope, list[str]] = Field(default_factory=lambda: {
        MemoryScope.PRIVATE: [],
        MemoryScope.TEAM: [],
        MemoryScope.BUSINESS: []
    })
    active_goals: list[str] = Field(default_factory=list)
    execution_history: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
