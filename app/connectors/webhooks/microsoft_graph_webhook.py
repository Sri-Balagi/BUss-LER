"""Microsoft Graph Subscription Manager

Manages webhook subscriptions (creating, renewing, deleting) for Microsoft Graph APIs.
"""

import structlog
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from app.connectors.builtin.communication.teams.graph_client import graph_request

logger = structlog.get_logger(__name__)

class MicrosoftGraphWebhookManager:
    
    @classmethod
    def create_subscription(
        cls, 
        token: str, 
        resource: str, 
        change_types: str, 
        notification_url: str, 
        client_state: str,
        expiry_minutes: int = 4230  # Default to max for many resources (just under 3 days)
    ) -> Dict[str, Any]:
        """Creates a new Graph API subscription."""
        expiry_time = (datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)).isoformat()
        
        payload = {
            "changeType": change_types,
            "notificationUrl": notification_url,
            "resource": resource,
            "expirationDateTime": expiry_time,
            "clientState": client_state
        }
        
        logger.info("Creating Graph subscription", resource=resource, notification_url=notification_url)
        return graph_request(token, "/subscriptions", method="POST", payload=payload)

    @classmethod
    def renew_subscription(cls, token: str, subscription_id: str, expiry_minutes: int = 4230) -> Dict[str, Any]:
        """Renews an existing Graph API subscription."""
        expiry_time = (datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)).isoformat()
        payload = {"expirationDateTime": expiry_time}
        logger.info("Renewing Graph subscription", subscription_id=subscription_id)
        return graph_request(token, f"/subscriptions/{subscription_id}", method="PATCH", payload=payload)

    @classmethod
    def delete_subscription(cls, token: str, subscription_id: str) -> None:
        """Deletes a Graph API subscription."""
        logger.info("Deleting Graph subscription", subscription_id=subscription_id)
        graph_request(token, f"/subscriptions/{subscription_id}", method="DELETE")

    @classmethod
    def list_subscriptions(cls, token: str) -> List[Dict[str, Any]]:
        """Lists active Graph API subscriptions."""
        res = graph_request(token, "/subscriptions", method="GET")
        return res.get("value", [])
