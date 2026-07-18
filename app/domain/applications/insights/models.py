import enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import UUID

from app.domain.applications.context.models import ApplicationContext
from app.domain.intelligence.capability import CapabilityType
from app.shared.events.models import DomainEvent


class InsightType(str, enum.Enum):
    ANOMALY = "ANOMALY"
    STRATEGIC_FORESIGHT = "STRATEGIC_FORESIGHT"
    PERFORMANCE_SUMMARY = "PERFORMANCE_SUMMARY"


class InsightExecutionRequest(BaseModel):
    """Specifies what capabilities are required to generate the insight."""
    required_capabilities: List[CapabilityType] = Field(..., description="Capabilities required for execution")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for insight generation")


class InsightContext(ApplicationContext):
    """Context for an insight generation job."""
    insight_type: InsightType = Field(..., description="The type of insight to generate")
    execution_request: InsightExecutionRequest = Field(..., description="The execution parameters and capabilities")


class InsightReport(BaseModel):
    """Canonical domain model for an insight report."""
    report_id: str = Field(..., description="Unique report identifier")
    schema_version: str = Field(default="1.0")
    tenant_id: Optional[str] = None
    generated_at: float = Field(default_factory=lambda: __import__("time").time())
    insight_type: InsightType
    title: str
    summary: str
    findings: List[str]
    recommendations: List[str]
    confidence: float
    supporting_evidence: Dict[str, Any]
    execution_metadata: Dict[str, Any]


class InsightGenerated(DomainEvent):
    """Domain event published after successful report generation."""
    report_id: str
    tenant_id: Optional[str]
    insight_type: InsightType
    execution_id: str
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
