from enum import StrEnum

from pydantic import BaseModel, Field


class IntentClassification(StrEnum):
    STRATEGIC_OBJECTIVE = "STRATEGIC_OBJECTIVE"
    OPERATIONAL_ADJUSTMENT = "OPERATIONAL_ADJUSTMENT"
    INFORMATION_RETRIEVAL = "INFORMATION_RETRIEVAL"
    ESCALATION = "ESCALATION"
    UNKNOWN = "UNKNOWN"


class IntentEntity(BaseModel):
    """An extracted entity from the user request."""

    entity_type: str
    value: str
    confidence: float = 1.0


class ExecutiveIntent(BaseModel):
    """Structured executive intent produced by the Intent Engine."""

    raw_request: str
    classification: IntentClassification = IntentClassification.UNKNOWN
    entities: list[IntentEntity] = Field(default_factory=list)
    requested_outcomes: list[str] = Field(default_factory=list)
    is_ambiguous: bool = False
    ambiguity_reason: str | None = None
