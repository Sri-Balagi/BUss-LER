import os
import urllib.request
import urllib.parse
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import structlog

from app.connectors.sdk.base import BaseConnector, ConnectorCapabilities, ConnectorOperatingMode
from app.connectors.sdk.canonical import CanonicalContact
from app.connectors.sdk.canonical import CanonicalMessage  # We would ideally import CanonicalSlackMessage but it's okay for now
from app.connectors.oauth.manager import OAuthProviderManager
from app.domain.shared.context import ExecutionContext

logger = structlog.get_logger(__name__)

class SlackConnector(BaseConnector):
    """Production Slack Connector using unified OAuth framework."""

    def __init__(self):
        self.oauth_manager = OAuthProviderManager()
        # Ensure we have our environment variables ready
        self.client_id = os.getenv("SLACK_OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("SLACK_OAUTH_CLIENT_SECRET", "")

    @property
    def connector_id(self) -> str:
        return "slack"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="slack",
            display_name="Slack",
            version="2.0.0",
            family="communication",
            supports_realtime=True,
            supports_polling=True,
            supported_actions=[
                "send_message",
                "send_direct_message",
                "read_channel_history",
                "list_channels",
                "upload_file",
                "add_reaction",
                "get_user_info",
                "health_check",
                "disconnect"
            ],
            required_scopes=[
                "channels:read",
                "channels:history",
                "groups:read",
                "groups:history",
                "chat:write",
                "im:read",
                "im:history",
                "im:write",
                "mpim:read",
                "mpim:history",
                "users:read",
                "reactions:write",
                "files:write"
            ],
            auth_type="oauth2",
            webhook_support=True,
            multi_account_support=True,
            operating_mode=ConnectorOperatingMode.PRODUCTION_OAUTH_MODE,
        )

    async def _get_access_token(self, tenant_id: str) -> str:
        return await self.oauth_manager.get_live_token(
            provider_id="slack", 
            tenant_id=tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def _slack_api_call(self, endpoint: str, token: str, payload: Optional[Dict] = None, method: str = "POST") -> Dict:
        url = f"https://slack.com/api/{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = None
        if payload is not None:
            if method == "GET":
                query_string = urllib.parse.urlencode(payload)
                url = f"{url}?{query_string}"
            else:
                data = json.dumps(payload).encode("utf-8")
                
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if not result.get("ok"):
                    logger.error(f"Slack API error on {endpoint}", error=result.get("error"))
                    raise ValueError(f"Slack API Error: {result.get('error')}")
                return result
        except Exception as exc:
            logger.error(f"Slack API request failed to {endpoint}", error=str(exc))
            raise exc

    async def execute_action(self, action: str, params: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        tenant_id = params.get("tenant_id", "default_tenant")
        token = await self._get_access_token(tenant_id)

        if action == "health_check":
            res = self._slack_api_call("auth.test", token, method="POST")
            return {"status": "ok", "team_id": res.get("team_id"), "user_id": res.get("user_id")}
            
        elif action == "list_channels":
            res = self._slack_api_call("conversations.list", token, {"types": "public_channel,private_channel"}, method="GET")
            channels = [{"id": c["id"], "name": c["name"], "is_member": c.get("is_member", False)} for c in res.get("channels", [])]
            return {"channels": channels}
            
        elif action == "send_message":
            channel = params.get("channel")
            text = params.get("text")
            res = self._slack_api_call("chat.postMessage", token, {"channel": channel, "text": text}, method="POST")
            msg = res.get("message", {})
            return {
                "message_id": msg.get("ts"),
                "channel_id": channel,
                "status": "SENT"
            }
            
        elif action == "send_direct_message":
            user_id = params.get("user_id")
            text = params.get("text")
            # Open DM conversation
            conv_res = self._slack_api_call("conversations.open", token, {"users": user_id}, method="POST")
            channel_id = conv_res["channel"]["id"]
            # Send message
            res = self._slack_api_call("chat.postMessage", token, {"channel": channel_id, "text": text}, method="POST")
            return {
                "message_id": res.get("message", {}).get("ts"),
                "channel_id": channel_id,
                "status": "SENT"
            }
            
        elif action == "read_channel_history":
            channel = params.get("channel")
            limit = params.get("limit", 10)
            res = self._slack_api_call("conversations.history", token, {"channel": channel, "limit": limit}, method="GET")
            messages = []
            for m in res.get("messages", []):
                messages.append({
                    "message_id": m.get("ts"),
                    "sender_id": m.get("user") or m.get("bot_id"),
                    "content": m.get("text"),
                    "timestamp": datetime.fromtimestamp(float(m.get("ts")), tz=timezone.utc).isoformat()
                })
            return {"messages": messages}
            
        elif action == "add_reaction":
            channel = params.get("channel")
            timestamp = params.get("timestamp")
            name = params.get("name") # emoji name
            self._slack_api_call("reactions.add", token, {"channel": channel, "timestamp": timestamp, "name": name}, method="POST")
            return {"status": "SUCCESS"}
            
        elif action == "disconnect":
            await self.oauth_manager.revoke_and_delete(
                provider_id="slack",
                tenant_id=tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            return {"status": "DISCONNECTED"}

        raise ValueError(f"Action {action} is not implemented for Slack connector")

    async def health_check(self) -> Dict[str, Any]:
        try:
            token = await self._get_access_token("default_tenant")
            res = self._slack_api_call("auth.test", token, method="POST")
            return {"status": "ok", "connector_id": self.connector_id, "team": res.get("team")}
        except Exception as e:
            return {"status": "error", "connector_id": self.connector_id, "error": str(e)}
