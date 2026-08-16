"""Salesforce OAuth Provider"""

import urllib.parse
from typing import List, Optional
import httpx
import structlog

from ..base_provider import BaseOAuthProvider, TokenResponse
from app.connectors.sdk.errors import ConnectorError

logger = structlog.get_logger(__name__)

_AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"
_TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"
_REVOKE_URL = "https://login.salesforce.com/services/oauth2/revoke"


class SalesforceOAuthProvider(BaseOAuthProvider):
    """Salesforce CRM OAuth provider."""

    provider_id = "salesforce"
    display_name = "Salesforce"
    auth_url_template = _AUTH_URL
    token_endpoint = _TOKEN_URL
    revoke_endpoint = _REVOKE_URL

    required_scopes: List[str] = [
        "api",
        "refresh_token",
        "offline_access"
    ]

    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        scopes_str = " ".join(self.required_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scopes_str,
            "state": state,
            "prompt": "login consent",
        }
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
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.token_endpoint, data=data, headers=headers)
            
            if resp.status_code != 200:
                logger.error("Salesforce token exchange failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to exchange Salesforce OAuth code: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=7200,  # Salesforce often doesn't return expires_in, defaults to 2h session
                scopes=json_resp.get("scope", "").split(" "),
                metadata={"instance_url": json_resp.get("instance_url"), "id": json_resp.get("id")}
            )

    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str) -> TokenResponse:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.token_endpoint, data=data, headers=headers)
            
            if resp.status_code != 200:
                logger.error("Salesforce token refresh failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to refresh Salesforce OAuth token: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token", refresh_token),
                expires_in=7200,
                scopes=json_resp.get("scope", "").split(" "),
                metadata={"instance_url": json_resp.get("instance_url"), "id": json_resp.get("id")}
            )

    async def revoke_token(self, token: str, client_id: str = "", client_secret: str = "") -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.revoke_endpoint, params={"token": token})
            if resp.status_code not in (200, 204):
                logger.warning("Salesforce token revocation might have failed", status_code=resp.status_code, response=resp.text)
