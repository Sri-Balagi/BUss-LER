import structlog
from app.connectors.webhooks.framework import WebhookReceiver
from app.connectors.webhooks.microsoft_graph_webhook import MicrosoftGraphWebhookManager
from .parser import parse_onenote_webhook

logger = structlog.get_logger(__name__)

class OneNoteWebhookSubscriber:
    """Manages Graph subscriptions for OneNote changes."""
    
    @classmethod
    def register(cls):
        WebhookReceiver.register_handler("microsoft_onenote", parse_onenote_webhook)

    @classmethod
    def subscribe_to_pages(cls, token: str, notification_url: str, client_state: str) -> str:
        """Subscribe to OneNote page creations and updates."""
        sub = MicrosoftGraphWebhookManager.create_subscription(
            token=token,
            resource="/me/onenote/pages",
            change_types="created,updated,deleted",
            notification_url=notification_url,
            client_state=client_state
        )
        return sub.get("id")

# Register handler on module import
OneNoteWebhookSubscriber.register()
