"""Canonical communication models."""
from __future__ import annotations
from datetime import datetime
from app.connectors.canonical.base import CanonicalObject


class CanonicalMessage(CanonicalObject):
    channel_id: str = ""
    sender_id: str = ""
    sender_name: str | None = None
    content: str = ""
    content_type: str = "text"  # text, html, markdown
    thread_id: str | None = None
    reply_to_id: str | None = None
    has_attachments: bool = False
    mentions: list[str] = []
    reactions: dict[str, int] = {}
    sent_at: datetime | None = None


class CanonicalConversation(CanonicalObject):
    subject: str = ""
    participants: list[str] = []
    message_count: int = 0
    last_message_at: datetime | None = None
    channel: str = ""  # "email", "slack", "teams", "whatsapp"


class CanonicalEmail(CanonicalObject):
    subject: str = ""
    sender: str = ""
    recipients: list[str] = []
    cc: list[str] = []
    bcc: list[str] = []
    body_text: str = ""
    body_html: str | None = None
    has_attachments: bool = False
    attachment_count: int = 0
    sent_at: datetime | None = None
    read: bool = False
    labels: list[str] = []
    thread_id: str | None = None
