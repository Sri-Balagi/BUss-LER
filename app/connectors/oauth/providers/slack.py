import urllib.parse
import urllib.request
import json
from typing import Optional

import structlog

from ..base_provider import BaseOAuthProvider, TokenResponse

logger = structlog.get_logger(__name__)

class SlackOAuthProvider(BaseOAuthProvider):
    provider_id = "slack"
    display_name = "Slack"
    auth_url_template = "https://slack.com/oauth/v2/authorize"
    token_endpoint = "https://slack.com/api/oauth.v2.access"
    revoke_endpoint = "https://slack.com/api/auth.revoke"
    required_scopes = [
        "channels:read",
        "channels:history",
        "chat:write",
        "im:read",
        "im:history",
        "im:write",
        "users:read",
        "reactions:write",
        "files:write",
        "files:read"
    ]

    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        params = {
            "client_id": client_id,
            "scope": ",".join(self.required_scopes),
            "redirect_uri": redirect_uri,
            "state": state
        }
        return f"{self.auth_url_template}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> TokenResponse:
        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(self.token_endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            
            if not resp_data.get("ok"):
                raise ValueError(f"Slack OAuth error: {resp_data.get('error')}")

            # Slack returns access_token (bot token) and authed_user (user token)
            # We primarily use the bot token for the connector.
            access_token = resp_data["access_token"]
            
            metadata = {
                "bot_user_id": resp_data.get("bot_user_id"),
                "app_id": resp_data.get("app_id"),
                "team": resp_data.get("team", {})
            }
            if "authed_user" in resp_data:
                metadata["authed_user"] = resp_data["authed_user"]

            return TokenResponse(
                access_token=access_token,
                refresh_token=None, # Slack typical bot tokens don't expire, unless token rotation is explicitly enabled
                expires_in=None,
                scopes=self.required_scopes,
                metadata=metadata
            )
        except Exception as exc:
            logger.error("Failed to exchange Slack OAuth code", error=str(exc))
            raise exc

    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str) -> TokenResponse:
        # Slack bot tokens don't expire by default unless rotation is enabled.
        # If enabled, refresh endpoint is the same token_endpoint with grant_type=refresh_token
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(self.token_endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            
            if not resp_data.get("ok"):
                raise ValueError(f"Slack refresh error: {resp_data.get('error')}")

            access_token = resp_data["access_token"]
            new_refresh_token = resp_data.get("refresh_token")
            expires_in = resp_data.get("expires_in")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token or refresh_token,
                expires_in=expires_in,
                scopes=self.required_scopes,
                metadata={}
            )
        except Exception as exc:
            logger.error("Failed to refresh Slack OAuth token", error=str(exc))
            raise exc

    async def revoke_token(self, token: str, client_id: str = "", client_secret: str = "") -> None:
        payload = {"token": token}
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(self.revoke_endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.warning("Failed to revoke Slack token", error=str(exc))
