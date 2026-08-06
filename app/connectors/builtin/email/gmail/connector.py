"""BizOS Gmail Connector"""

import json
import base64
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict

import structlog

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities
from app.connectors.oauth.manager import OAuthProviderManager
from app.domain.shared.context import ExecutionContext
from .manifest import MANIFEST
from .mapper import map_gmail_to_canonical

logger = structlog.get_logger(__name__)

class GmailConnector(BaseConnector):
    def __init__(self):
        self.oauth_manager = OAuthProviderManager()

    @property
    def connector_id(self) -> str:
        return MANIFEST.connector_id

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(**MANIFEST.model_dump())

    async def _get_access_token(self, tenant_id: str, account_id: str) -> str:
        """Fetch the Google token from the OAuth Manager."""
        return await self.oauth_manager.get_live_token("google", tenant_id, account_id)

    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        tenant_id = context.tenant_id or "default_tenant"
        account_id = params.get("account_id", "default")
        
        try:
            access_token = await self._get_access_token(tenant_id, account_id)
        except ValueError as e:
            logger.warning("No access token available for Gmail", tenant_id=tenant_id, account_id=account_id)
            return {"status": "FAILED", "error": "Authentication required", "details": str(e)}

        if action == "send_email":
            return await self._send_email(params, access_token)
        elif action == "read_inbox":
            return await self._read_inbox(params, access_token)
            
        return {"status": "UNSUPPORTED_ACTION", "action": action}

    async def _send_email(self, params: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        recipient = params.get("to") or params.get("recipient", "")
        subject = params.get("subject", "BizOS Notification")
        body = params.get("body") or params.get("message", "")

        mime_msg = MIMEMultipart()
        mime_msg["to"] = recipient
        mime_msg["subject"] = subject
        mime_msg.attach(MIMEText(body, "plain"))
        raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = json.dumps({"raw": raw_b64}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            canonical = map_gmail_to_canonical(resp_data)
            return {
                "status": "EXECUTED",
                "connector": self.connector_id,
                "action": "send_email",
                "canonical_email": canonical.model_dump(),
            }
        except Exception as exc:
            logger.error("Failed to send email via Gmail", error=str(exc))
            return {"status": "FAILED", "error": str(exc)}

    async def _read_inbox(self, params: Dict[str, Any], access_token: str) -> Dict[str, Any]:
        limit = params.get("limit", 10)
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={limit}"
        headers = {"Authorization": f"Bearer {access_token}"}
        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            
            emails = []
            for msg in resp_data.get("messages", []):
                msg_id = msg.get("id")
                # Fetch full message
                msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
                msg_req = urllib.request.Request(msg_url, headers=headers, method="GET")
                with urllib.request.urlopen(msg_req, timeout=10) as msg_resp:
                    full_msg = json.loads(msg_resp.read().decode("utf-8"))
                    emails.append(map_gmail_to_canonical(full_msg).model_dump())

            return {
                "status": "EXECUTED",
                "connector": self.connector_id,
                "action": "read_inbox",
                "emails": emails,
            }
        except Exception as exc:
            logger.error("Failed to read inbox via Gmail", error=str(exc))
            return {"status": "FAILED", "error": str(exc)}

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "connector_id": self.connector_id,
        }
