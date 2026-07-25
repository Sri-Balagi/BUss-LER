"""Facebook Messenger Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="messenger",
    name="Facebook Messenger Connector",
    version="1.0.0",
    description="Facebook Messenger Platform API integration for Page messages.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["pages_messaging"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="messenger.messaging",
            name="Facebook Messenger",
            description="Send and receive Messenger messages for Facebook Pages",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["messenger.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Facebook Messenger for Page communications.",
        business_vocabulary=["facebook", "messenger", "page", "chat"],
        natural_language_aliases=["FB Messenger", "Messenger"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["facebook", "messenger", "chat"],
        pricing="free",
    ),
)
