from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class HeuristicStatus(str, Enum):
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
    heuristics: List[Heuristic] = Field(default_factory=list)
