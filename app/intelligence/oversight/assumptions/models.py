from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class AssumptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    VALIDATED = "VALIDATED"
    INVALIDATED = "INVALIDATED"

class Assumption(BaseModel):
    assumption_id: str
    description: str
    status: AssumptionStatus = AssumptionStatus.ACTIVE
    supporting_evidence_ids: list[str] = Field(default_factory=list)

class AssumptionRegistry(BaseModel):
    """Tracks assumptions made during reasoning."""
    registry_id: str
    assumptions: list[Assumption] = Field(default_factory=list)
