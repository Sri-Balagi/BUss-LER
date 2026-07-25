"""Presence and Typing frameworks."""
from __future__ import annotations
from app.connectors.canonical.messaging import CanonicalPresence, CanonicalTypingEvent


class PresenceManager:
    """Manages presence status queries and state synchronization."""

    def create_presence(self, user_id: str, status: str = "online", status_text: str | None = None) -> CanonicalPresence:
        return CanonicalPresence(
            source_connector="presence_manager",
            source_id=user_id,
            user_id=user_id,
            status=status,
            status_text=status_text,
        )


class TypingHandler:
    """Manages typing indicator events."""

    def create_typing_event(self, conversation_id: str, user_id: str, is_typing: bool = True) -> CanonicalTypingEvent:
        return CanonicalTypingEvent(
            source_connector="typing_handler",
            source_id=conversation_id,
            conversation_id=conversation_id,
            user_id=user_id,
            is_typing=is_typing,
        )
