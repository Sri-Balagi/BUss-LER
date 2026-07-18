import enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.planning.models import Goal, Plan


class AgentStatus(str, enum.Enum):
    """Lifecycle status of the cognitive agent execution."""
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    RETRIEVING = "RETRIEVING"
    REASONING = "REASONING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REFLECTING = "REFLECTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReflectionFeedback(str, enum.Enum):
    """Immediate evaluation feedback emitted by the reflection step."""
    IS_COMPLETE = "IS_COMPLETE"
    NEEDS_REPLAN = "NEEDS_REPLAN"
    NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
    FAILED = "FAILED"


class AgentState(IntelligenceContext):
    """
    Context tracked throughout the agent cognitive cycle.
    Inherits from IntelligenceContext to act as the primary operational context.
    """
    agent_id: UUID
    current_goal: Optional[Goal] = None
    active_plan: Optional[Plan] = None
    current_iteration: int = Field(default=0)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    reflection_feedback: Optional[ReflectionFeedback] = None
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    
    # We allow some fields to be mutated as this represents the agent's internal state machine
    class Config:
        frozen = False


class IAgentImplementation(IIntelligenceProvider):
    """
    The base provider capability representing the core agent persona and rules.
    Agents are resolved exclusively through the Capability Registry.
    """
    pass
