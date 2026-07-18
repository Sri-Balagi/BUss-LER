from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

from app.shared.enums import AgentType, AgentStatus

class Capability(BaseModel):
    """
    Value object representing an agent's capability.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)

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
    capabilities: List[Capability] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
