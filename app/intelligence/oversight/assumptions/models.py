from enum import StrEnum

from pydantic import BaseModel, Field


class AssumptionStatus(StrEnum):
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
