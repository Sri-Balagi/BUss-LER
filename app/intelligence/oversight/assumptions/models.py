from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class AssumptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VALIDATED = "VALIDATED"
    INVALIDATED = "INVALIDATED"

class Assumption(BaseModel):
    assumption_id: str
    description: str
    status: AssumptionStatus = AssumptionStatus.ACTIVE
    supporting_evidence_ids: List[str] = Field(default_factory=list)

class AssumptionRegistry(BaseModel):
    """Tracks assumptions made during reasoning."""
    registry_id: str
    assumptions: List[Assumption] = Field(default_factory=list)
