import json
from typing import Dict, Any
from app.connectors.webhooks.framework import CanonicalWebhookEvent

def parse_todo_webhook(payload_bytes: bytes, headers: Dict[str, str]) -> CanonicalWebhookEvent:
    """Parses raw Graph webhook notification for To Do changes (Future compatibility)."""
    data = json.loads(payload_bytes.decode("utf-8"))
    
    notifications = data.get("value", [])
    if not notifications:
        raise ValueError("Empty webhook payload")
        
    notification = notifications[0]
    
    return CanonicalWebhookEvent(
        event_id=notification.get("subscriptionId", "unknown"),
        provider_id="microsoft_todo",
        event_type=notification.get("changeType", "updated"),
        resource_id=notification.get("resource", ""),
        data={
            "clientState": notification.get("clientState"),
            "resourceData": notification.get("resourceData"),
            "tenantId": notification.get("tenantId")
        }
    )
