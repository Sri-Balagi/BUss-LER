from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class ConvergenceStatus(str, Enum):
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
    metrics: List[StabilityMetric] = Field(default_factory=list)
