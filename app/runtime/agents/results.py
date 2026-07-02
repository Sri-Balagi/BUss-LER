from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Status of an agent's execution outcome."""

    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"


class AgentResult(BaseModel):
    """
    Structured outcome of an agent's execution.
    Returned to the consumer (e.g., Scheduler/Supervisor).
    """

    status: AgentStatus = Field(description="Final status of the execution")
    outputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured outputs produced by the agent"
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict, description="Execution metrics (e.g., duration, tokens used)"
    )
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings encountered")
    errors: list[str] = Field(
        default_factory=list, description="Fatal or critical errors encountered"
    )
