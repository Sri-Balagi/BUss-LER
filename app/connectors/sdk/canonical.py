"""Canonical BizOS Domain Objects

Translates all provider-specific REST responses (Google, Stripe, Razorpay, Open Banking)
into standardized, strongly-typed BizOS domain models.
No raw provider JSON leaks outside the connector layer.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CanonicalEmail(BaseModel):
    """Normalized email domain object."""
    email_id: str
    thread_id: Optional[str] = None
    sender: str
    recipients: List[str]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    snippet: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "google_workspace"


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
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    status: str = "confirmed"
    raw_provider_id: str = "google_calendar"


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
    """Normalized instant messaging object (WhatsApp, Slack, Meta)."""
    message_id: str
    channel_id: str
    sender_id: str
    sender_name: Optional[str] = None
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str


class CanonicalContact(BaseModel):
    """Normalized contact / CRM profile object."""
    contact_id: str
    display_name: str
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    organization: Optional[str] = None
    raw_provider_id: str
