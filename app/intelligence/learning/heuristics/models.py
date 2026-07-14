from enum import StrEnum

from pydantic import BaseModel, Field


class HeuristicStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    PROPOSED = "PROPOSED"


class HeuristicConfidence(BaseModel):
    score: float
    data_points: int


class Heuristic(BaseModel):
    heuristic_id: str
    rule_description: str
    confidence: HeuristicConfidence
    status: HeuristicStatus = HeuristicStatus.ACTIVE


class HeuristicCatalog(BaseModel):
    """Catalog of derived business rules and shortcuts."""

    catalog_id: str
    heuristics: list[Heuristic] = Field(default_factory=list)
