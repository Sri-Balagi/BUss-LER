from pydantic import BaseModel, Field
from typing import List

class EvidenceWeight(BaseModel):
    evidence_id: str
    weight: float

class ConfidenceScore(BaseModel):
    category: str
    score: float

class ConfidenceAssessment(BaseModel):
    """Aggregate confidence score for a decision or plan."""
    overall_score: float
    scores: List[ConfidenceScore] = Field(default_factory=list)
    evidence_weights: List[EvidenceWeight] = Field(default_factory=list)
    is_actionable: bool
