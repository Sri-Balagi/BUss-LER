"""Canonical BizOS Domain Objects

Translates all provider-specific REST responses (Google, Stripe, Razorpay, Open Banking,
Microsoft 365) into standardized, strongly-typed BizOS domain models.
No raw provider JSON leaks outside the connector layer.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CanonicalEmail(BaseModel):
    """Normalized email domain object."""
    email_id: str
    thread_id: Optional[str] = None
    conversation_id: Optional[str] = None
    sender: str
    recipients: List[str]
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)
    subject: str
    body_text: str
    body_html: Optional[str] = None
    snippet: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    folder: Optional[str] = None
    is_read: bool = True
    is_flagged: bool = False
    importance: str = "normal"  # low, normal, high
    has_attachments: bool = False
    attachment_ids: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "microsoft_outlook"


class CanonicalAttachment(BaseModel):
    """Normalized email/message attachment object."""
    attachment_id: str
    parent_id: str  # email_id or message_id this belongs to
    name: str
    content_type: str
    size_bytes: Optional[int] = None
    content_bytes: Optional[str] = None  # base64 encoded for small attachments
    download_url: Optional[str] = None
    is_inline: bool = False
    raw_provider_id: str


class CanonicalFile(BaseModel):
    """Normalized file / drive object."""
    file_id: str
    name: str
    mime_type: str
    size_bytes: Optional[int] = None
    web_view_link: Optional[str] = None
    download_url: Optional[str] = None
    parents: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "google_drive"


class CanonicalCalendarEvent(BaseModel):
    """Normalized calendar event object."""
    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: List[str] = Field(default_factory=list)
    attendee_statuses: Dict[str, str] = Field(default_factory=dict)  # email -> accepted/declined/tentative
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    is_online_meeting: bool = False
    calendar_id: Optional[str] = None
    organizer: Optional[str] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled
    recurrence: Optional[str] = None
    raw_provider_id: str = "microsoft_calendar"


class CanonicalFinancialAccount(BaseModel):
    """Normalized banking / financial account object."""
    account_id: str
    account_name: str
    account_type: str  # checking, savings, credit, merchant_balance
    currency: str = "INR"
    available_balance: float
    current_balance: float
    institution_name: str
    routing_or_ifsc: Optional[str] = None
    account_number_masked: str
    raw_provider_id: str


class CanonicalTransaction(BaseModel):
    """Normalized banking / payment transaction object."""
    transaction_id: str
    account_id: str
    amount: float
    currency: str = "INR"
    type: str  # DEBIT, CREDIT
    category: Optional[str] = None
    description: str
    counterparty: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "SETTLED"  # SETTLED, PENDING, FAILED
    raw_provider_id: str


class CanonicalPayment(BaseModel):
    """Normalized payment intent / checkout object."""
    payment_id: str
    amount: float
    currency: str = "INR"
    status: str  # CREATED, AUTHORIZED, CAPTURED, FAILED, REFUNDED
    customer_email: Optional[str] = None
    description: Optional[str] = None
    payment_method: str  # UPI, CARD, NETBANKING, OAUTH
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str


class CanonicalMessage(BaseModel):
    """Normalized instant messaging object (WhatsApp, Slack, Teams, Meta)."""
    message_id: str
    channel_id: str
    sender_id: str
    sender_name: Optional[str] = None
    content: str
    content_html: Optional[str] = None
    thread_id: Optional[str] = None
    reply_to_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    reactions: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    raw_provider_id: str


class CanonicalContact(BaseModel):
    """Normalized contact / CRM profile object."""
    contact_id: str
    display_name: str
    given_name: Optional[str] = None
    surname: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    organization: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    raw_provider_id: str


class CanonicalConversation(BaseModel):
    """Normalized chat conversation / thread object."""
    conversation_id: str
    topic: Optional[str] = None
    conversation_type: str = "group"  # group, oneOnOne, channel
    participants: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: Optional[datetime] = None
    raw_provider_id: str


class CanonicalTeam(BaseModel):
    """Normalized Teams/workspace object."""
    team_id: str
    display_name: str
    description: Optional[str] = None
    visibility: str = "private"  # private, public
    is_archived: bool = False
    member_count: Optional[int] = None
    web_url: Optional[str] = None
    raw_provider_id: str = "microsoft_teams"


class CanonicalChannel(BaseModel):
    """Normalized Teams channel / Slack channel object."""
    channel_id: str
    team_id: Optional[str] = None
    display_name: str
    description: Optional[str] = None
    channel_type: str = "standard"  # standard, private, shared
    is_archived: bool = False
    is_member: bool = False
    member_count: Optional[int] = None
    web_url: Optional[str] = None
    raw_provider_id: str


class CanonicalPresence(BaseModel):
    """Normalized user presence / availability object."""
    user_id: str
    availability: str  # Available, Away, Busy, DoNotDisturb, Offline, Unknown
    activity: Optional[str] = None
    out_of_office_message: Optional[str] = None
    raw_provider_id: str = "microsoft_teams"


class CanonicalMeetingTranscript(BaseModel):
    """Normalized meeting transcript / recording metadata object."""
    transcript_id: str
    meeting_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    duration_seconds: Optional[int] = None
    raw_provider_id: str = "microsoft_teams"


class CanonicalSlackMessage(CanonicalMessage):
    workspace_id: str
    channel_name: Optional[str] = None
    thread_ts: Optional[str] = None
    reactions: List[str] = Field(default_factory=list)
    raw_provider_id: str = "slack"


class CanonicalTeamsMessage(CanonicalMessage):
    team_id: Optional[str] = None
    channel_name: Optional[str] = None
    importance: str = "normal"
    web_url: Optional[str] = None
    raw_provider_id: str = "microsoft_teams"


class CanonicalDriveItem(BaseModel):
    """Normalized Microsoft OneDrive file / folder object."""
    item_id: str
    name: str
    item_type: str  # file, folder
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    parent_path: Optional[str] = None
    web_url: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    etag: Optional[str] = None
    ctag: Optional[str] = None
    version: Optional[str] = None
    raw_provider_id: str = "microsoft_onedrive"


class CanonicalTodoTask(BaseModel):
    """Normalized Microsoft To Do task object."""
    task_id: str
    list_id: str
    title: str
    status: str  # notStarted, inProgress, completed, waitingOnOthers, deferred
    importance: str = "normal"  # low, normal, high
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    body: Optional[str] = None
    reminder_at: Optional[datetime] = None
    recurrence: Optional[Dict[str, Any]] = None
    categories: List[str] = Field(default_factory=list)
    checklist_items: List[Dict[str, Any]] = Field(default_factory=list)
    linked_resources: List[Dict[str, Any]] = Field(default_factory=list)
    raw_provider_id: str = "microsoft_todo"


class CanonicalNote(BaseModel):
    """Normalized OneNote page object."""
    note_id: str
    notebook_id: str
    section_id: str
    section_name: Optional[str] = None
    title: str
    content_html: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    web_url: Optional[str] = None
    self_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    raw_provider_id: str = "microsoft_onenote"


class CanonicalPerson(BaseModel):
    """Normalized Microsoft Graph People object."""
    person_id: str
    display_name: str
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    job_title: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    relevance_score: Optional[float] = None
    relationship: Optional[str] = None
    source: Optional[str] = None
    raw_provider_id: str = "microsoft_people"


class AssociationType(str, Enum):
    CONTACT_TO_COMPANY = "CONTACT_TO_COMPANY"
    DEAL_TO_COMPANY = "DEAL_TO_COMPANY"
    DEAL_TO_CONTACT = "DEAL_TO_CONTACT"
    DEAL_TO_PRODUCT = "DEAL_TO_PRODUCT"
    NOTE_TO_CONTACT = "NOTE_TO_CONTACT"
    NOTE_TO_DEAL = "NOTE_TO_DEAL"
    TASK_TO_CONTACT = "TASK_TO_CONTACT"
    TASK_TO_DEAL = "TASK_TO_DEAL"
    GENERIC = "GENERIC"


class CanonicalAssociation(BaseModel):
    """Provider-agnostic relationship binding between any two business entities."""
    association_id: str
    provider: str
    from_resource_type: str
    from_resource_id: str
    to_resource_type: str
    to_resource_id: str
    association_type: AssociationType = AssociationType.GENERIC
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CanonicalCompany(BaseModel):
    """Normalized CRM Company / Account object."""
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


class CanonicalLead(BaseModel):
    """Normalized CRM Lead / Prospect object."""
    lead_id: str
    provider: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[str] = None
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
    stage_id: str
    pipeline_id: str = "default"
    close_date: Optional[datetime] = None
    company_id: Optional[str] = None
    contact_ids: List[str] = Field(default_factory=list)
    owner_id: Optional[str] = None
    probability: Optional[float] = None
    is_closed: bool = False
    is_won: bool = False
    associations: List[CanonicalAssociation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class CanonicalOpportunity(CanonicalDeal):
    """Alias for CanonicalDeal representing an Opportunity."""
    pass


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
    resource_type: str = "deals"
    stages: List[CanonicalStage] = Field(default_factory=list)


class CanonicalActivityType(str, Enum):
    CALL = "CALL"
    MEETING = "MEETING"
    EMAIL = "EMAIL"
    SMS = "SMS"
    NOTE = "NOTE"


class CanonicalActivity(BaseModel):
    """Normalized logged engagement activity (including CRM notes)."""
    activity_id: str
    provider: str
    activity_type: CanonicalActivityType
    title: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    associated_contact_ids: List[str] = Field(default_factory=list)
    associated_deal_id: Optional[str] = None
    owner_id: Optional[str] = None


class CanonicalOwner(BaseModel):
    """Normalized system user or rep assigned in CRM."""
    owner_id: str
    provider: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

