"""Canonical messaging domain extensions."""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any
from pydantic import Field
from app.connectors.canonical.base import CanonicalObject


class CanonicalAttachment(CanonicalObject):
    file_name: str = ""
    mime_type: str = ""
    file_size_bytes: int = 0
    url: str = ""
    thumbnail_url: str | None = None
    media_type: str = "document"  # image, video, audio, document


class CanonicalReaction(CanonicalObject):
    message_id: str = ""
    emoji: str = ""
    user_id: str = ""
    added_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CanonicalContact(CanonicalObject):
    phone_number: str | None = None
    email: str | None = None
    name: str = ""
    avatar_url: str | None = None
    status_message: str | None = None


class CanonicalGroup(CanonicalObject):
    name: str = ""
    description: str | None = None
    member_count: int = 0
    members: list[str] = Field(default_factory=list)
    avatar_url: str | None = None


class CanonicalPresence(CanonicalObject):
    user_id: str = ""
    status: str = "offline"  # online, offline, away, busy
    status_text: str | None = None
    last_seen_at: datetime | None = None


class CanonicalDeliveryReceipt(CanonicalObject):
    message_id: str = ""
    recipient_id: str = ""
    status: str = "sent"  # sent, delivered, read, failed
    delivered_at: datetime | None = None
    read_at: datetime | None = None


class CanonicalTypingEvent(CanonicalObject):
    conversation_id: str = ""
    user_id: str = ""
    is_typing: bool = True
