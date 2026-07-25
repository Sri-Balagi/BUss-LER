"""Twilio Connector Implementation."""
from __future__ import annotations
from typing import Any
from app.connectors.sdk.messaging.base import BaseMessagingConnector
from app.connectors.canonical.message import CanonicalMessage


class TwilioConnector(BaseMessagingConnector):
    """Twilio Messaging API connector implementation."""

    def __init__(self, connector_id: str = "twilio", profile_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(connector_id=connector_id, profile_id=profile_id)

    def get_capabilities(self) -> list[str]:
        return ["twilio.messaging"]

    async def install(self) -> None: pass
    async def uninstall(self) -> None: pass
    async def connect(self) -> None: pass
    async def disconnect(self) -> None: pass
    async def authenticate(self) -> None: pass
    async def refresh_token(self) -> None: pass
    async def validate(self) -> Any: pass
    async def health_check(self) -> Any: pass
    async def sync(self, sync_type: Any = None) -> Any: pass
    async def handle_webhook(self, payload: dict[str, Any]) -> Any: pass
    async def shutdown(self) -> None: pass

    async def send_message(
        self,
        recipient_id: str,
        content: str,
        media_url: str | None = None,
    ) -> CanonicalMessage:
        return CanonicalMessage(
            source_connector=self.connector_id,
            source_id="SM_twilio_1001",
            channel_id=recipient_id,
            sender_id="twilio_sender",
            content=content,
        )

    async def reply_message(
        self,
        conversation_id: str,
        message_id: str,
        content: str,
    ) -> CanonicalMessage:
        return CanonicalMessage(
            source_connector=self.connector_id,
            source_id="SM_twilio_1002",
            channel_id=conversation_id,
            sender_id="twilio_sender",
            content=content,
            reply_to_id=message_id,
        )
