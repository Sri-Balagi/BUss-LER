"""Google Workspace OAuth Provider"""

import urllib.parse
from typing import List, Optional, Dict, Any
import httpx
import structlog

from ..base_provider import BaseOAuthProvider, TokenResponse
from app.connectors.sdk.errors import ConnectorError

logger = structlog.get_logger(__name__)

_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_REVOKE_URL = "https://oauth2.googleapis.com/revoke"


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google Workspace OAuth provider for Gmail, Drive, Calendar, Docs, Sheets."""

    provider_id = "google"
    display_name = "Google Workspace"
    auth_url_template = _AUTH_URL
    token_endpoint = _TOKEN_URL
    revoke_endpoint = _REVOKE_URL

    required_scopes: List[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.activity.readonly",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        scopes_str = " ".join(self.required_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scopes_str,
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        # Add optional login_hint if passed
        login_hint = kwargs.get("login_hint") or kwargs.get("email")
        if login_hint:
            params["login_hint"] = login_hint

        query_string = urllib.parse.urlencode(params)
        return f"{self.auth_url_template}?{query_string}"

    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> TokenResponse:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.token_endpoint, data=data)
            
            if resp.status_code != 200:
                logger.error("Google token exchange failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to exchange Google OAuth code: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in"),
                scopes=json_resp.get("scope", "").split(" "),
                metadata={"id_token": json_resp.get("id_token")}
            )

    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str) -> TokenResponse:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.token_endpoint, data=data)
            
            if resp.status_code != 200:
                logger.error("Google token refresh failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to refresh Google OAuth token: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token", refresh_token),  # Google often doesn't return a new refresh token
                expires_in=json_resp.get("expires_in"),
                scopes=json_resp.get("scope", "").split(" "),
                metadata={"id_token": json_resp.get("id_token")}
            )

    async def revoke_token(self, token: str, client_id: str = "", client_secret: str = "") -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.revoke_endpoint, params={"token": token})
            if resp.status_code not in (200, 204):
                logger.warning("Google token revocation might have failed", status_code=resp.status_code, response=resp.text)
