from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.connectors.sdk.canonical.common import CanonicalAssociation


class CanonicalContact(BaseModel):
    """Normalized CRM Contact object."""
    contact_id: str
    provider: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[str] = None
    job_title: Optional[str] = None
    lifecycle_stage: Optional[str] = None       # "lead", "subscriber", "opportunity", "customer"
    lead_status: Optional[str] = None           # "NEW", "OPEN", "IN_PROGRESS", "QUALIFIED", "UNQUALIFIED"
    owner_id: Optional[str] = None
    associations: List[CanonicalAssociation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class CanonicalCompany(BaseModel):
    """Normalized CRM Company object."""
    company_id: str
    provider: str
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    number_of_employees: Optional[int] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    owner_id: Optional[str] = None
    associations: List[CanonicalAssociation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class CanonicalDeal(BaseModel):
    """Normalized CRM Deal / Opportunity object."""
    deal_id: str
    provider: str
    title: str
    amount: float = 0.0
    currency: str = "USD"
    stage_id: str                                # "QUALIFIED", "PROPOSAL", "CLOSED_WON", "CLOSED_LOST"
    pipeline_id: str = "default"
    close_date: Optional[datetime] = None
    company_id: Optional[str] = None
    contact_ids: List[str] = Field(default_factory=list)
    owner_id: Optional[str] = None
    probability: Optional[float] = None          # 0.0 to 1.0
    is_closed: bool = False
    is_won: bool = False
    associations: List[CanonicalAssociation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class CanonicalStage(BaseModel):
    """Normalized pipeline stage definition."""
    stage_id: str
    label: str
    display_order: int = 0
    probability: float = 0.0
    is_closed: bool = False
    is_won: bool = False


class CanonicalPipeline(BaseModel):
    """Normalized sales or support pipeline."""
    pipeline_id: str
    provider: str
    label: str
    resource_type: str = "deals"                # "deals" | "tickets"
    stages: List[CanonicalStage] = Field(default_factory=list)


class CanonicalTask(BaseModel):
    """Normalized CRM Task / Action item."""
    task_id: str
    provider: str
    subject: str
    body: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "NOT_STARTED"                 # "NOT_STARTED", "IN_PROGRESS", "COMPLETED", "DEFERRED"
    priority: str = "MEDIUM"                     # "LOW", "MEDIUM", "HIGH"
    associated_contact_id: Optional[str] = None
    associated_deal_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CanonicalNote(BaseModel):
    """Normalized CRM Note / Activity Log."""
    note_id: str
    provider: str
    body: str
    associated_contact_id: Optional[str] = None
    associated_deal_id: Optional[str] = None
    associated_company_id: Optional[str] = None
    author_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CanonicalActivityType(str, Enum):
    CALL = "CALL"
    MEETING = "MEETING"
    EMAIL = "EMAIL"
    SMS = "SMS"


class CanonicalActivity(BaseModel):
    """Normalized logged engagement activity."""
    activity_id: str
    provider: str
    activity_type: CanonicalActivityType
    title: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    associated_contact_ids: List[str] = Field(default_factory=list)
    associated_deal_id: Optional[str] = None
    owner_id: Optional[str] = None


class CanonicalProduct(BaseModel):
    """Normalized product catalog entry."""
    product_id: str
    provider: str
    name: str
    sku: Optional[str] = None
    price: float = 0.0
    currency: str = "USD"
    description: Optional[str] = None


class CanonicalOwner(BaseModel):
    """Normalized system user or rep assigned in CRM."""
    owner_id: str
    provider: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
