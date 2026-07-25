"""Telegram Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="telegram",
    name="Telegram Connector",
    version="1.0.0",
    description="Telegram Bot API integration for group chats, channels, and direct bot messages.",
    author="BizOS Core Team",
    auth_type=AuthType.API_KEY,
    capabilities=[
        CapabilityDeclaration(
            capability_id="telegram.messaging",
            name="Telegram Messaging",
            description="Send messages and media to Telegram chats and channels",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["telegram.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    supports_polling=True,
    ai_metadata=AIMetadata(
        description="Integrates Telegram Bot API for group and channel messaging.",
        business_vocabulary=["telegram", "bot", "channel", "group", "chat"],
        natural_language_aliases=["Telegram", "Telegram Bot"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["telegram", "bot", "chat"],
        pricing="free",
    ),
)
