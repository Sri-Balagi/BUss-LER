import structlog
from app.connectors.webhooks.framework import WebhookReceiver
from .parser import parse_todo_webhook

logger = structlog.get_logger(__name__)

class TodoWebhookSubscriber:
    """Stub for To Do webhook subscriptions.
    
    Microsoft Graph does not currently support change notifications (webhooks) 
    for To Do tasks (only for Outlook Tasks). This module exists for future
    compatibility and architectural consistency.
    """
    
    @classmethod
    def register(cls):
        # We register the handler in case support is added and webhooks start arriving
        WebhookReceiver.register_handler("microsoft_todo", parse_todo_webhook)

    @classmethod
    def subscribe(cls, token: str, notification_url: str, client_state: str) -> str:
        logger.warning("Microsoft To Do does not currently support Graph subscriptions.")
        return "unsupported"

# Register handler on module import
TodoWebhookSubscriber.register()
