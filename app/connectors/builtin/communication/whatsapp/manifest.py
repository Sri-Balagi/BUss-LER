"""WhatsApp Business Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="whatsapp",
    name="WhatsApp Business Connector",
    version="1.0.0",
    description="WhatsApp Business Cloud API integration for direct customer messaging and templates.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["whatsapp_business_messaging", "whatsapp_business_management"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="whatsapp.messaging",
            name="WhatsApp Messaging",
            description="Send and receive WhatsApp text, media, and template messages",
            operations=["send_message", "reply_message", "send_template"],
            canonical_model="CanonicalMessage",
            tool_ids=["whatsapp.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent", "MessageDeliveredEvent", "MessageReadEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates WhatsApp Business for direct customer conversations.",
        business_vocabulary=["whatsapp", "phone", "chat", "template", "message"],
        natural_language_aliases=["WhatsApp", "WA", "WhatsApp Business"],
        supported_operations=["send_message", "send_template"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["whatsapp", "messaging", "chat"],
        pricing="free",
    ),
)
