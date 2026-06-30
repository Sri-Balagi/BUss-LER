from typing import List

from pydantic import BaseModel, Field


class EvidenceWeight(BaseModel):
    evidence_id: str
    weight: float

class ConfidenceScore(BaseModel):
    category: str
    score: float

class ConfidenceAssessment(BaseModel):
    """Aggregate confidence score for a decision or plan."""
    overall_score: float
    scores: list[ConfidenceScore] = Field(default_factory=list)
    evidence_weights: list[EvidenceWeight] = Field(default_factory=list)
    is_actionable: bool
