from typing import Any
from pydantic import BaseModel, Field


class ObservationResult(BaseModel):
    """Result of evaluating workflow execution outcomes against goal targets."""
    goal_progress: float = 0.0
    state_changes: list[str] = Field(default_factory=list)
    policy_valid: bool = True
    success_criteria_met: bool = True
    metrics: dict[str, Any] = Field(default_factory=dict)
    should_replan: bool = False
    failure_analysis: str | None = None
