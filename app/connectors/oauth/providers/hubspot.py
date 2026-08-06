"""HubSpot OAuth Provider"""

import urllib.parse
from typing import List, Optional
import httpx
import structlog

from ..base_provider import BaseOAuthProvider, TokenResponse
from app.connectors.sdk.errors import ConnectorError

logger = structlog.get_logger(__name__)

_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"


class HubSpotOAuthProvider(BaseOAuthProvider):
    """HubSpot CRM OAuth provider."""

    provider_id = "hubspot"
    display_name = "HubSpot"
    auth_url_template = _AUTH_URL
    token_endpoint = _TOKEN_URL
    revoke_endpoint = None  # HubSpot has a different process for revoking apps, usually done via API key or UI

    required_scopes: List[str] = [
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.companies.read",
        "crm.objects.companies.write",
        "crm.objects.deals.read",
        "crm.objects.deals.write",
        "crm.objects.owners.read",
        "crm.lists.read",
        "crm.schemas.custom.read",
        "oauth",
        "tickets",
        "sales-email-read"
    ]

    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        scopes_str = " ".join(self.required_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scopes_str,
            "state": state,
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
                logger.error("HubSpot token exchange failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to exchange HubSpot OAuth code: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token"),
                expires_in=json_resp.get("expires_in"),
                scopes=self.required_scopes,
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
                logger.error("HubSpot token refresh failed", status_code=resp.status_code, response=resp.text)
                raise ConnectorError(f"Failed to refresh HubSpot OAuth token: {resp.text}")
                
            json_resp = resp.json()
            return TokenResponse(
                access_token=json_resp.get("access_token", ""),
                refresh_token=json_resp.get("refresh_token", refresh_token),
                expires_in=json_resp.get("expires_in"),
                scopes=self.required_scopes,
            )
