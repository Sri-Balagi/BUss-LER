from enum import StrEnum

from pydantic import BaseModel, Field


class ConvergenceStatus(StrEnum):
    CONVERGED = "CONVERGED"
    OSCILLATING = "OSCILLATING"
    STAGNANT = "STAGNANT"
    PROGRESSING = "PROGRESSING"


class StabilityMetric(BaseModel):
    metric_name: str
    value: float


class ConvergenceAssessment(BaseModel):
    """Evaluates whether the reasoning process has reached a stable conclusion."""

    status: ConvergenceStatus
    confidence: float
    metrics: list[StabilityMetric] = Field(default_factory=list)
