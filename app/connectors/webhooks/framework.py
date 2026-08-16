"""BizOS Generic Webhook Receiver & Validation Framework

Generic webhook reception pipeline:
WebhookReceiver → Signature Validator → Canonical Normalization → Event Bus → Workflow Engine
"""

import hmac
import hashlib
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class CanonicalWebhookEvent(BaseModel):
    """Standardized canonical webhook payload dispatched to Event Bus."""
    event_id: str
    provider_id: str
    event_type: str
    resource_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookValidator:
    """Signature validation helper for webhooks."""

    @staticmethod
    def verify_hmac_sha256(payload_body: bytes, signature: str, secret: str) -> bool:
        if not secret or not signature:
            return False
        expected = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected.lower(), signature.lower())


class WebhookReceiver:
    """Universal Webhook Handler Registry."""

    _handlers: Dict[str, Callable[[bytes, Dict[str, str]], CanonicalWebhookEvent]] = {}

    @classmethod
    def register_handler(
        cls, provider_id: str, handler: Callable[[bytes, Dict[str, str]], CanonicalWebhookEvent]
    ) -> None:
        cls._handlers[provider_id] = handler
        logger.info("Registered webhook handler for provider", provider_id=provider_id)

    @classmethod
    def process_webhook(
        cls, provider_id: str, payload_bytes: bytes, headers: Dict[str, str]
    ) -> CanonicalWebhookEvent:
        if provider_id not in cls._handlers:
            raise ValueError(f"No webhook handler registered for provider '{provider_id}'")

        handler = cls._handlers[provider_id]
        event = handler(payload_bytes, headers)

        logger.info(
            "Processed canonical webhook event",
            provider_id=provider_id,
            event_id=event.event_id,
            event_type=event.event_type,
        )

        return event
