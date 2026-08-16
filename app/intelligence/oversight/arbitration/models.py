from enum import Enum

from pydantic import BaseModel, Field

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutivePlan


class ArbitrationReason(str, Enum):
    HIGHER_CONFIDENCE = "HIGHER_CONFIDENCE"
    BETTER_STRATEGIC_ALIGNMENT = "BETTER_STRATEGIC_ALIGNMENT"
    LOWER_RISK = "LOWER_RISK"
    RESOURCE_EFFICIENCY = "RESOURCE_EFFICIENCY"


class ArbitrationDecision(BaseModel):
    """Result of choosing between competing valid decisions or plans."""

    arbitration_id: str
    selected_decision: ExecutiveDecision | None = None
    selected_plan: ExecutivePlan | None = None
    reason: ArbitrationReason
    rationale: str
    discarded_decision_ids: list[str] = Field(default_factory=list)
    discarded_plan_ids: list[str] = Field(default_factory=list)
