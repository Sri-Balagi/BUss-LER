"""Google Workspace Parent Auth Provider & Token Lifecycle Manager

Manages bundled OAuth2 token scope exchange, token refresh via Google Auth endpoints,
and secure storage in ConnectorAuthVault.
Serves Gmail, Google Drive, Google Calendar, and future Google services (Docs, Sheets, Meet, Contacts).
"""

import time
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import structlog

from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.sdk.permissions import ConnectorPermission

logger = structlog.get_logger(__name__)

GOOGLE_WORKSPACE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar",
]


class GoogleWorkspaceAuthProvider:
    """Manages authentication and access token lifecycle for the Google Workspace ecosystem."""

    @classmethod
    def get_auth_url(cls, client_id: str, redirect_uri: str, state: str) -> str:
        """Generates Google OAuth2 authorization URL requesting bundled workspace scopes."""
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_WORKSPACE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    @classmethod
    async def exchange_code_and_store(
        cls,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
    ) -> Dict[str, Any]:
        """Exchanges OAuth code for tokens and persists them securely in ConnectorAuthVault."""
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            access_token = resp_data["access_token"]
            refresh_token = resp_data.get("refresh_token")
            expires_in = resp_data.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            # Store in ConnectorAuthVault
            ConnectorAuthVault.set_tokens(
                provider_id="google_workspace",
                tenant_id=tenant_id,
                account_id=account_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scopes=GOOGLE_WORKSPACE_SCOPES,
            )

            logger.info("Successfully exchanged and vaulted Google Workspace OAuth tokens", tenant_id=tenant_id)
            return {
                "status": "SUCCESS",
                "provider_id": "google_workspace",
                "expires_at": expires_at.isoformat(),
                "scopes": GOOGLE_WORKSPACE_SCOPES,
            }
        except Exception as exc:
            logger.error("Failed to exchange Google OAuth code", error=str(exc))
            raise exc

    @classmethod
    async def refresh_workspace_tokens(
        cls,
        client_id: str,
        client_secret: str,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
    ) -> Dict[str, Any]:
        """Refreshes expired access tokens using the offline refresh token."""
        stored = ConnectorAuthVault.get_tokens("google_workspace", tenant_id, account_id)
        if not stored or not stored.get("refresh_token"):
            return {"status": "NO_REFRESH_TOKEN_AVAILABLE"}

        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": stored["refresh_token"],
            "grant_type": "refresh_token",
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))

            new_access_token = resp_data["access_token"]
            expires_in = resp_data.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            ConnectorAuthVault.set_tokens(
                provider_id="google_workspace",
                tenant_id=tenant_id,
                account_id=account_id,
                access_token=new_access_token,
                refresh_token=stored["refresh_token"],  # Retain refresh token
                expires_at=expires_at,
                scopes=stored.get("scopes", GOOGLE_WORKSPACE_SCOPES),
            )
            logger.info("Refreshed Google Workspace access token", tenant_id=tenant_id)
            return {"status": "REFRESHED", "expires_at": expires_at.isoformat()}
        except Exception as exc:
            logger.error("Failed to refresh Google Workspace access token", error=str(exc))
            return {"status": "FAILED", "error": str(exc)}
