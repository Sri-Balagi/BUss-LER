"""BizOS Canonical Domain Objects — Phase 2 Production Grade

Translates all provider-specific REST responses into standardized, strongly-typed
BizOS domain models. No raw provider JSON ever leaks outside the connector layer.

Providers → Canonical models:
  Google Drive      → CanonicalFile, CanonicalFolder, CanonicalPermission,
                       CanonicalRevision, CanonicalComment, CanonicalDriveActivity
  Google Calendar   → CanonicalCalendarEvent, CanonicalCalendar, CanonicalFreeBusy,
                       CanonicalCalendarAttachment
  Microsoft OneDrive→ CanonicalFile, CanonicalFolder, CanonicalPermission,
                       CanonicalRevision, CanonicalDeltaChange
  SharePoint        → CanonicalFile, CanonicalFolder, CanonicalSharePointSite,
                       CanonicalSharePointList, CanonicalSharePointListItem
  Notion            → CanonicalNotionPage, CanonicalNotionDatabase,
                       CanonicalNotionBlock, CanonicalNotionUser
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Shared Primitives ────────────────────────────────────────────────────────


class CanonicalUser(BaseModel):
    """Normalized user/principal object across all providers."""
    user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_provider_id: str


class CanonicalPage(BaseModel):
    """Generic paginated result wrapper."""
    items: List[Any]
    next_page_token: Optional[str] = None
    total_count: Optional[int] = None
    has_more: bool = False


# ── Communication (Phase 1 — kept for compatibility) ─────────────────────────


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


# ── File System (Drive / OneDrive / SharePoint) ───────────────────────────────


class CanonicalFile(BaseModel):
    """Normalized file object — Google Drive, OneDrive, SharePoint document library."""
    file_id: str
    name: str
    mime_type: str
    size_bytes: Optional[int] = None
    web_view_link: Optional[str] = None
    download_url: Optional[str] = None
    parents: List[str] = Field(default_factory=list)
    owners: List[CanonicalUser] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_by: Optional[CanonicalUser] = None
    is_trashed: bool = False
    is_shared: bool = False
    starred: bool = False
    description: Optional[str] = None
    version: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    etag: Optional[str] = None
    raw_provider_id: str


class CanonicalFolder(BaseModel):
    """Normalized folder / directory object."""
    folder_id: str
    name: str
    parents: List[str] = Field(default_factory=list)
    web_view_link: Optional[str] = None
    item_count: Optional[int] = None
    is_shared: bool = False
    is_root: bool = False
    drive_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str


class CanonicalDrive(BaseModel):
    """Normalized drive / shared drive object."""
    drive_id: str
    name: str
    drive_type: str = "user"  # user, shared, personal, business
    theme_color_rgb: Optional[str] = None
    restrictions: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str


class CanonicalPermission(BaseModel):
    """Normalized ACL permission entry for any resource."""
    permission_id: str
    resource_id: str
    resource_type: str  # file, folder, drive, site, list
    role: str  # owner, organizer, writer, commenter, reader
    grantee_type: str  # user, group, domain, anyone
    grantee_email: Optional[str] = None
    grantee_domain: Optional[str] = None
    allow_file_discovery: bool = False
    inherited: bool = False
    expiration_time: Optional[datetime] = None
    raw_provider_id: str


class CanonicalRevision(BaseModel):
    """Normalized file version / revision entry."""
    revision_id: str
    file_id: str
    modified_at: datetime
    modified_by: Optional[CanonicalUser] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    download_url: Optional[str] = None
    keep_forever: bool = False
    is_current: bool = False
    raw_provider_id: str


class CanonicalComment(BaseModel):
    """Normalized comment on a file, page, or document."""
    comment_id: str
    resource_id: str
    resource_type: str  # file, page, database
    content: str
    author: Optional[CanonicalUser] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    is_resolved: bool = False
    replies: List["CanonicalComment"] = Field(default_factory=list)
    raw_provider_id: str


class CanonicalDeltaChange(BaseModel):
    """Normalized delta sync change record."""
    change_id: str
    resource_id: str
    resource_type: str
    change_type: str  # created, modified, deleted, moved, renamed
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_by: Optional[CanonicalUser] = None
    old_parent_id: Optional[str] = None
    new_parent_id: Optional[str] = None
    resource_snapshot: Optional[Dict[str, Any]] = None
    raw_provider_id: str


class CanonicalWebhookSubscription(BaseModel):
    """Normalized webhook / push notification subscription."""
    subscription_id: str
    resource_id: Optional[str] = None
    resource_type: str
    webhook_url: str
    event_types: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
    state: str = "active"  # active, expired, cancelled
    raw_provider_id: str


class CanonicalDriveActivity(BaseModel):
    """Normalized Drive Activity API entry."""
    activity_id: str
    action_type: str  # create, edit, move, delete, rename, comment, permission_change, etc.
    actor: Optional[CanonicalUser] = None
    targets: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "google_drive"


# ── Calendar ─────────────────────────────────────────────────────────────────


class CanonicalCalendar(BaseModel):
    """Normalized calendar object."""
    calendar_id: str
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    time_zone: str = "UTC"
    color_id: Optional[str] = None
    background_color: Optional[str] = None
    is_primary: bool = False
    access_role: str = "reader"  # owner, writer, reader, freeBusyReader
    etag: Optional[str] = None
    raw_provider_id: str = "google_calendar"


class CanonicalCalendarAttachment(BaseModel):
    """Normalized attachment on a calendar event."""
    file_id: Optional[str] = None
    file_url: str
    title: str
    mime_type: Optional[str] = None
    icon_url: Optional[str] = None
    raw_provider_id: str


class CanonicalCalendarEvent(BaseModel):
    """Normalized calendar event object — Google Calendar, Outlook Calendar."""
    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_all_day: bool = False
    timezone: str = "UTC"
    attendees: List[str] = Field(default_factory=list)
    organizer: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    conference_data: Optional[Dict[str, Any]] = None
    status: str = "confirmed"  # confirmed, tentative, cancelled
    visibility: str = "default"  # default, public, private, confidential
    recurrence: Optional[List[str]] = None
    recurring_event_id: Optional[str] = None
    attachments: List[CanonicalCalendarAttachment] = Field(default_factory=list)
    reminders: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    etag: Optional[str] = None
    html_link: Optional[str] = None
    raw_provider_id: str = "google_calendar"


class CanonicalFreeBusy(BaseModel):
    """Normalized free/busy availability slot."""
    calendar_id: str
    user_email: Optional[str] = None
    busy_slots: List[Dict[str, datetime]] = Field(default_factory=list)
    time_min: datetime
    time_max: datetime
    errors: List[Dict[str, str]] = Field(default_factory=list)
    raw_provider_id: str = "google_calendar"


# ── SharePoint ────────────────────────────────────────────────────────────────


class CanonicalSharePointSite(BaseModel):
    """Normalized SharePoint site / subsite object."""
    site_id: str
    name: str
    display_name: str
    web_url: str
    description: Optional[str] = None
    is_root: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "sharepoint"


class CanonicalSharePointList(BaseModel):
    """Normalized SharePoint list / document library object."""
    list_id: str
    name: str
    display_name: str
    description: Optional[str] = None
    list_type: str = "genericList"  # genericList, documentLibrary, events, tasks, etc.
    item_count: int = 0
    web_url: Optional[str] = None
    is_document_library: bool = False
    site_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "sharepoint"


class CanonicalSharePointListItem(BaseModel):
    """Normalized SharePoint list item."""
    item_id: str
    list_id: str
    site_id: str
    fields: Dict[str, Any] = Field(default_factory=dict)
    web_url: Optional[str] = None
    etag: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_by: Optional[CanonicalUser] = None
    raw_provider_id: str = "sharepoint"


# ── Notion ───────────────────────────────────────────────────────────────────


class CanonicalNotionUser(BaseModel):
    """Normalized Notion user object."""
    user_id: str
    object_type: str = "user"
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    user_type: str = "person"  # person, bot
    raw_provider_id: str = "notion"


class CanonicalNotionPage(BaseModel):
    """Normalized Notion page object."""
    page_id: str
    object_type: str = "page"
    title: str = ""
    url: str
    archived: bool = False
    parent_type: str = "workspace"  # workspace, database_id, page_id, block_id
    parent_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    cover: Optional[Dict[str, Any]] = None
    icon: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[CanonicalNotionUser] = None
    modified_by: Optional[CanonicalNotionUser] = None
    raw_provider_id: str = "notion"


class CanonicalNotionDatabase(BaseModel):
    """Normalized Notion database object."""
    database_id: str
    object_type: str = "database"
    title: str = ""
    url: str
    archived: bool = False
    is_inline: bool = False
    parent_type: str = "workspace"
    parent_id: Optional[str] = None
    properties_schema: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    cover: Optional[Dict[str, Any]] = None
    icon: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "notion"


class CanonicalNotionBlock(BaseModel):
    """Normalized Notion block object (any block type)."""
    block_id: str
    object_type: str = "block"
    block_type: str  # paragraph, heading_1, bulleted_list_item, table, image, etc.
    parent_id: str
    parent_type: str  # block_id, page_id, database_id, workspace
    has_children: bool = False
    archived: bool = False
    content: Dict[str, Any] = Field(default_factory=dict)
    children: List["CanonicalNotionBlock"] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str = "notion"


# ── Financial (Phase 1 — kept for compatibility) ──────────────────────────────


class CanonicalFinancialAccount(BaseModel):
    """Normalized banking / financial account object."""
    account_id: str
    account_name: str
    account_type: str
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
    type: str
    category: Optional[str] = None
    description: str
    counterparty: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "SETTLED"
    raw_provider_id: str


class CanonicalPayment(BaseModel):
    """Normalized payment intent / checkout object."""
    payment_id: str
    amount: float
    currency: str = "INR"
    status: str
    customer_email: Optional[str] = None
    description: Optional[str] = None
    payment_method: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_provider_id: str


# ── Resolve forward references ────────────────────────────────────────────────
CanonicalComment.model_rebuild()
CanonicalNotionBlock.model_rebuild()
