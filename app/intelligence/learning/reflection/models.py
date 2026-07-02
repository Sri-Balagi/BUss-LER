from enum import Enum

from pydantic import BaseModel, Field


class ReflectionSeverity(str, Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SIGNIFICANT = "SIGNIFICANT"


class ReflectionFinding(BaseModel):
    finding_id: str
    description: str
    severity: ReflectionSeverity
    is_weakness: bool


class ReflectionReport(BaseModel):
    """Structured reflection on a completed reasoning cycle."""

    report_id: str
    cycle_id: str
    findings: list[ReflectionFinding] = Field(default_factory=list)
