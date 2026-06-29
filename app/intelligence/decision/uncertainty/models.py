from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class UncertaintySource(str, Enum):
    MISSING_DATA = "MISSING_DATA"
    STALE_DATA = "STALE_DATA"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    UNPROVEN_ASSUMPTION = "UNPROVEN_ASSUMPTION"

class Assumption(BaseModel):
    assumption_id: str
    description: str
    confidence_level: float

class UncertaintyAssessment(BaseModel):
    """Estimation of missing or unproven information."""
    overall_uncertainty_score: float
    sources: List[UncertaintySource] = Field(default_factory=list)
    assumptions: List[Assumption] = Field(default_factory=list)
    missing_evidence_ids: List[str] = Field(default_factory=list)
