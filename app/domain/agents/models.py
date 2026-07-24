import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.shared.enums import AgentStatus, AgentType


class Capability(BaseModel):
    """
    Value object representing an agent's capability.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0.0"
    metadata: dict[str, Any] = Field(default_factory=dict)

class Agent(BaseModel):
    """
    First-class Agent Domain model.
    Represents an AI actor registered within BizOS.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0.0"
    status: AgentStatus = AgentStatus.REGISTERED
    agent_type: AgentType
    capabilities: list[Capability] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
