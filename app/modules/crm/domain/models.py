"""CRM Domain entities and value objects leveraging Shared Domain Kernel models."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.kernel.kernel_models import Customer, Money, Organization


class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"
    CONVERTED = "CONVERTED"


class DealStage(str, Enum):
    PROSPECTING = "PROSPECTING"
    QUALIFICATION = "QUALIFICATION"
    NEEDS_ANALYSIS = "NEEDS_ANALYSIS"
    VALUE_PROPOSITION = "VALUE_PROPOSITION"
    PROPOSAL_SENT = "PROPOSAL_SENT"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class Lead(BaseModel):
    """Inbound sales lead entity."""

    lead_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    first_name: str
    last_name: str
    company_name: str | None = None
    email: str
    phone: str | None = None
    status: LeadStatus = LeadStatus.NEW
    source: str = "Website Inbound"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SalesOpportunity(BaseModel):
    """Sales Opportunity / Deal aggregate root."""

    opportunity_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    title: str
    customer: Customer  # Reuses Shared Domain Kernel Customer model
    organization: Organization | None = None
    deal_value: Money
    stage: DealStage = DealStage.PROSPECTING
    probability_percent: float = 20.0
    assigned_sales_rep: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expected_close_date: datetime | None = None


class ActivityLog(BaseModel):
    """Sales activity log (calls, emails, meetings)."""

    activity_id: UUID = Field(default_factory=uuid4)
    opportunity_id: UUID | None = None
    customer_id: UUID | None = None
    activity_type: str  # EMAIL, CALL, MEETING, NOTE
    subject: str
    notes: str | None = None
    logged_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerSegment(BaseModel):
    """Target customer segment container."""

    segment_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    criteria: dict[str, Any] = Field(default_factory=dict)


class SalesAnalytics(BaseModel):
    """Metric container for CRM Sales Pipeline & Win Rate analytics."""

    total_pipeline_value: Money
    weighted_pipeline_value: Money
    total_deals: int
    closed_won_deals: int
    closed_lost_deals: int
    win_rate_percentage: float
    target_win_rate_percentage: float = 30.0
    pipeline_velocity_days: float = 45.0
    recommendation: str | None = None
