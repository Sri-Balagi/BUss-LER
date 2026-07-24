import enum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.applications.context.models import ApplicationContext
from app.domain.intelligence.capability import CapabilityType
from app.shared.events.models import DomainEvent


class InsightType(enum.StrEnum):
    ANOMALY = "ANOMALY"
    STRATEGIC_FORESIGHT = "STRATEGIC_FORESIGHT"
    PERFORMANCE_SUMMARY = "PERFORMANCE_SUMMARY"


class InsightExecutionRequest(BaseModel):
    """Specifies what capabilities are required to generate the insight."""
    required_capabilities: list[CapabilityType] = Field(..., description="Capabilities required for execution")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Parameters for insight generation")


class InsightContext(ApplicationContext):
    """Context for an insight generation job."""
    insight_type: InsightType = Field(..., description="The type of insight to generate")
    execution_request: InsightExecutionRequest = Field(..., description="The execution parameters and capabilities")


class InsightReport(BaseModel):
    """Canonical domain model for an insight report."""
    report_id: str = Field(..., description="Unique report identifier")
    schema_version: str = Field(default="1.0")
    tenant_id: str | None = None
    generated_at: float = Field(default_factory=lambda: __import__("time").time())
    insight_type: InsightType
    title: str
    summary: str
    findings: list[str]
    recommendations: list[str]
    confidence: float
    supporting_evidence: dict[str, Any]
    execution_metadata: dict[str, Any]


class InsightGenerated(DomainEvent):
    """Domain event published after successful report generation."""
    report_id: str
    tenant_id: str | None
    insight_type: InsightType
    execution_id: str
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
