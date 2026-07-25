"""Twilio Messaging Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="twilio",
    name="Twilio Messaging Connector",
    version="1.0.0",
    description="Twilio REST API integration for SMS, MMS, and WhatsApp messaging.",
    author="BizOS Core Team",
    auth_type=AuthType.API_KEY,
    capabilities=[
        CapabilityDeclaration(
            capability_id="twilio.messaging",
            name="Twilio Messaging",
            description="Send SMS, MMS, and WhatsApp messages via Twilio API",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["twilio.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent", "MessageDeliveredEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Twilio SMS, MMS, and WhatsApp channels.",
        business_vocabulary=["twilio", "sms", "text", "mms", "phone"],
        natural_language_aliases=["Twilio", "SMS Gateway"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["twilio", "sms", "whatsapp"],
        pricing="free",
    ),
)
