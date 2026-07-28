from enum import Enum

from pydantic import BaseModel, Field


class SuccessScore(str, Enum):
    ACHIEVED = "ACHIEVED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class OutcomeMetric(BaseModel):
    metric_name: str
    target_value: float
    actual_value: float


class OutcomeEvaluation(BaseModel):
    """Evaluates the outcomes of executed plans against objectives."""

    evaluation_id: str
    plan_id: str
    overall_score: SuccessScore
    metrics: list[OutcomeMetric] = Field(default_factory=list)
