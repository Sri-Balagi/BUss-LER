"""Modular Messaging SDK Framework."""
from __future__ import annotations
from abc import abstractmethod
from typing import Any
from app.connectors.sdk.base import BaseConnector, SyncResult, SyncType, WebhookResult
from app.connectors.canonical.message import CanonicalMessage


class BaseMessagingConnector(BaseConnector):
    """Abstract base class for all messaging connectors in the Communication Suite."""

    @abstractmethod
    async def send_message(
        self,
        recipient_id: str,
        content: str,
        media_url: str | None = None,
    ) -> CanonicalMessage:
        """Send a text or media message to a user or channel."""

    @abstractmethod
    async def reply_message(
        self,
        conversation_id: str,
        message_id: str,
        content: str,
    ) -> CanonicalMessage:
        """Reply to a specific message thread."""

    async def list_conversations(self) -> list[dict[str, Any]]:
        """List active conversations or channels."""
        return []

    async def get_presence(self, user_id: str) -> str:
        """Get online presence status for a user."""
        return "unknown"
