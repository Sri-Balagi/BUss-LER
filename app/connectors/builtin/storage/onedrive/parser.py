import json
from typing import Dict, Any
from app.connectors.webhooks.framework import CanonicalWebhookEvent

def parse_onedrive_webhook(payload_bytes: bytes, headers: Dict[str, str]) -> CanonicalWebhookEvent:
    """Parses raw Graph webhook notification for OneDrive changes."""
    data = json.loads(payload_bytes.decode("utf-8"))
    
    # Graph webhook payloads are wrapped in a 'value' array
    notifications = data.get("value", [])
    if not notifications:
        raise ValueError("Empty webhook payload")
        
    # We take the first one for the CanonicalWebhookEvent (batching could be handled higher up)
    notification = notifications[0]
    
    # Validation against subscription state (clientState) is usually done at the webhook router layer,
    # but we extract it here for completeness
    client_state = notification.get("clientState")
    
    # Extract the resource path (e.g. /me/drive/root)
    resource = notification.get("resource", "")
    
    return CanonicalWebhookEvent(
        event_id=notification.get("subscriptionId", "unknown"),
        provider_id="microsoft_onedrive",
        event_type=notification.get("changeType", "updated"),
        resource_id=resource,
        data={
            "clientState": client_state,
            "resourceData": notification.get("resourceData"),
            "tenantId": notification.get("tenantId")
        }
    )
