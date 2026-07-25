"""
Connector domain events.

All connector events are published on the BizOS SystemBus under the
``connector.*`` topic namespace. Business modules and AI agents subscribe
to these events without coupling to connector implementations.

Event Naming Convention:
    connector.<connector_id>.<action>

    e.g. connector.github.issue_created
         connector.gmail.email_received
         connector.stripe.payment_completed
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel


class ConnectorEvent(DomainBaseModel):
    """Base class for all connector-emitted domain events."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    connector_id: str
    profile_id: str = "default"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str | None = None
    source: str = "bizos-connector"
    version: str = "1.0"

    @property
    def topic(self) -> str:
        """SystemBus topic for this event."""
        return f"connector.{self.connector_id}.{self.__class__.__name__.lower()}"


# ---------------------------------------------------------------------------
# Lifecycle Events
# ---------------------------------------------------------------------------


class ConnectorInstalledEvent(ConnectorEvent):
    """Emitted when a connector is successfully installed."""
    manifest_version: str


class ConnectorUninstalledEvent(ConnectorEvent):
    """Emitted when a connector is uninstalled."""


class ConnectorConnectedEvent(ConnectorEvent):
    """Emitted when a connector establishes a live connection."""


class ConnectorDisconnectedEvent(ConnectorEvent):
    """Emitted when a connector loses or drops its connection."""
    reason: str = ""


class ConnectorAuthenticatedEvent(ConnectorEvent):
    """Emitted when authentication succeeds."""
    auth_type: str


class ConnectorTokenRefreshedEvent(ConnectorEvent):
    """Emitted when an OAuth token is refreshed."""


class ConnectorHealthChangedEvent(ConnectorEvent):
    """Emitted when a connector's health status changes."""
    previous_status: str
    new_status: str
    healthy: bool
    latency_ms: float | None = None


class ConnectorErrorEvent(ConnectorEvent):
    """Emitted when a connector encounters an unrecoverable error."""
    error_type: str
    error_message: str
    operation: str = ""


# ---------------------------------------------------------------------------
# Sync Events
# ---------------------------------------------------------------------------


class ConnectorSyncStartedEvent(ConnectorEvent):
    """Emitted when a sync cycle begins."""
    sync_type: str


class ConnectorSyncCompletedEvent(ConnectorEvent):
    """Emitted when a sync cycle completes successfully."""
    sync_type: str
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    duration_ms: float | None = None


class ConnectorSyncFailedEvent(ConnectorEvent):
    """Emitted when a sync cycle fails."""
    sync_type: str
    error: str
    records_processed: int = 0


# ---------------------------------------------------------------------------
# Webhook Events
# ---------------------------------------------------------------------------


class WebhookReceivedEvent(ConnectorEvent):
    """Emitted when an inbound webhook payload is received and verified."""
    event_type: str
    webhook_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload_size_bytes: int = 0


class WebhookProcessedEvent(ConnectorEvent):
    """Emitted when a webhook payload is successfully processed."""
    event_type: str
    webhook_id: str


class WebhookFailedEvent(ConnectorEvent):
    """Emitted when a webhook payload cannot be processed."""
    event_type: str
    webhook_id: str
    error: str


# ---------------------------------------------------------------------------
# Communication Events
# ---------------------------------------------------------------------------


class EmailReceivedEvent(ConnectorEvent):
    """Emitted when a new email is received (Gmail, Outlook, etc.)."""
    message_id: str
    subject: str
    sender: str
    recipient: str
    has_attachments: bool = False
    canonical_id: str | None = None


class MessageReceivedEvent(ConnectorEvent):
    """Emitted when a chat message is received (Slack, Teams, WhatsApp, etc.)."""
    message_id: str
    channel_id: str
    sender_id: str
    content_preview: str = ""
    canonical_id: str | None = None


class CalendarEventCreatedEvent(ConnectorEvent):
    """Emitted when a new calendar event is created or detected."""
    calendar_event_id: str
    title: str
    start_time: datetime
    end_time: datetime | None = None
    canonical_id: str | None = None


# ---------------------------------------------------------------------------
# Project Management Events
# ---------------------------------------------------------------------------


class IssueCreatedEvent(ConnectorEvent):
    """Emitted when an issue is created (GitHub, GitLab, Jira, etc.)."""
    issue_id: str
    title: str
    assignee: str | None = None
    labels: list[str] = Field(default_factory=list)
    canonical_id: str | None = None


class IssueUpdatedEvent(ConnectorEvent):
    """Emitted when an issue is updated."""
    issue_id: str
    changes: dict[str, Any] = Field(default_factory=dict)
    canonical_id: str | None = None


class IssueClosedEvent(ConnectorEvent):
    """Emitted when an issue is closed or resolved."""
    closed_issue_id: str
    resolution: str = ""
    canonical_id: str | None = None


class PullRequestCreatedEvent(ConnectorEvent):
    """Emitted when a pull request or merge request is opened."""
    pr_id: str
    title: str
    author: str
    base_branch: str
    head_branch: str
    canonical_id: str | None = None


class PullRequestMergedEvent(ConnectorEvent):
    """Emitted when a pull request is merged."""
    pr_id: str
    merged_by: str
    canonical_id: str | None = None


# ---------------------------------------------------------------------------
# Finance Events
# ---------------------------------------------------------------------------


class PaymentCompletedEvent(ConnectorEvent):
    """Emitted when a payment is successfully processed (Stripe, Razorpay, etc.)."""
    payment_id: str
    amount: float
    currency: str
    customer_id: str | None = None
    canonical_id: str | None = None


class PaymentFailedEvent(ConnectorEvent):
    """Emitted when a payment attempt fails."""
    payment_id: str
    amount: float
    currency: str
    failure_reason: str = ""
    canonical_id: str | None = None


class InvoiceCreatedEvent(ConnectorEvent):
    """Emitted when a new invoice is generated."""
    invoice_id: str
    amount_due: float
    currency: str
    customer_id: str | None = None
    canonical_id: str | None = None


class OrderCreatedEvent(ConnectorEvent):
    """Emitted when a new order is placed (Shopify, ERP, etc.)."""
    order_id: str
    total_amount: float
    currency: str
    customer_id: str | None = None
    item_count: int = 0
    canonical_id: str | None = None


# ---------------------------------------------------------------------------
# CRM Events
# ---------------------------------------------------------------------------


class ContactCreatedEvent(ConnectorEvent):
    """Emitted when a new contact is created in a CRM."""
    contact_id: str
    name: str
    email: str | None = None
    canonical_id: str | None = None


class LeadCreatedEvent(ConnectorEvent):
    """Emitted when a new lead is created (Salesforce, HubSpot, etc.)."""
    lead_id: str
    name: str
    source: str = ""
    canonical_id: str | None = None


class OpportunityUpdatedEvent(ConnectorEvent):
    """Emitted when a CRM opportunity is updated."""
    opportunity_id: str
    stage: str
    amount: float | None = None
    canonical_id: str | None = None


# ---------------------------------------------------------------------------
# Storage Events
# ---------------------------------------------------------------------------


class FileUploadedEvent(ConnectorEvent):
    """Emitted when a file is uploaded (Google Drive, Dropbox, etc.)."""
    file_id: str
    file_name: str
    file_size_bytes: int = 0
    mime_type: str = ""
    canonical_id: str | None = None


class FileDeletedEvent(ConnectorEvent):
    """Emitted when a file is deleted from cloud storage."""
    file_id: str
    file_name: str
    canonical_id: str | None = None
