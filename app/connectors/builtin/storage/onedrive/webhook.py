import structlog
from app.connectors.webhooks.framework import WebhookReceiver
from app.connectors.webhooks.microsoft_graph_webhook import MicrosoftGraphWebhookManager
from .parser import parse_onedrive_webhook

logger = structlog.get_logger(__name__)

class OneDriveWebhookSubscriber:
    """Manages Graph subscriptions for OneDrive changes."""
    
    @classmethod
    def register(cls):
        WebhookReceiver.register_handler("microsoft_onedrive", parse_onedrive_webhook)

    @classmethod
    def subscribe_to_root(cls, token: str, notification_url: str, client_state: str) -> str:
        """Subscribe to changes in the user's root drive."""
        # Drive supports 'updated' as the only changeType for root tracking
        sub = MicrosoftGraphWebhookManager.create_subscription(
            token=token,
            resource="/me/drive/root",
            change_types="updated",
            notification_url=notification_url,
            client_state=client_state
        )
        return sub.get("id")

# Register handler on module import
OneDriveWebhookSubscriber.register()
