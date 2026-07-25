"""Slack Communication Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="slack",
    name="Slack Connector",
    version="1.0.0",
    description="Slack Web API and Events API integration for team chat, channels, and threads.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["chat:write", "channels:read", "channels:history", "users:read"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="slack.messaging",
            name="Slack Messaging",
            description="Send messages, create threads, and list channels",
            operations=["send_message", "reply_message", "list_conversations"],
            canonical_model="CanonicalMessage",
            tool_ids=["slack.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent", "MessageSentEvent"],
    supported_sync_types=[SyncType.FULL, SyncType.INCREMENTAL],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Slack workspace channels, threads, and direct messages.",
        business_vocabulary=["slack", "channel", "thread", "message", "workspace"],
        natural_language_aliases=["Slack", "Slack Chat"],
        supported_operations=["send_message", "reply_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["slack", "chat", "team"],
        pricing="free",
    ),
)
