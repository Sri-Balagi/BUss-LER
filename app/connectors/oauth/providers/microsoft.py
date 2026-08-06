"""Microsoft 365 OAuth Provider

Covers both Outlook (Mail, Calendar, Contacts) and Microsoft Teams
via a single Microsoft Graph application registration.
Uses the /common (multi-tenant) endpoint.
"""

import urllib.parse
import urllib.request
import json
from typing import List, Optional

import structlog

from ..base_provider import BaseOAuthProvider, TokenResponse

logger = structlog.get_logger(__name__)

# Microsoft Graph OAuth endpoints (multi-tenant)
_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


class MicrosoftOAuthProvider(BaseOAuthProvider):
    """Unified Microsoft 365 OAuth provider for Outlook + Teams."""

    provider_id = "microsoft"
    display_name = "Microsoft 365"
    auth_url_template = _AUTH_URL
    token_endpoint = _TOKEN_URL
    revoke_endpoint = None  # Microsoft uses token expiry — no explicit revoke endpoint for delegated tokens

    required_scopes: List[str] = [
        # Identity
        "openid",
        "profile",
        "email",
        "offline_access",
        # Outlook — Mail
        "Mail.Read",
        "Mail.ReadWrite",
        "Mail.Send",
        "MailboxSettings.Read",
        # Outlook — Contacts
        "Contacts.Read",
        "Contacts.ReadWrite",
        # Outlook — Calendar
        "Calendars.Read",
        "Calendars.ReadWrite",
        "Calendars.ReadWrite.Shared",
        # User & People
        "User.Read",
        "People.Read",
        # Teams
        "Team.ReadBasic.All",
        "Channel.ReadBasic.All",
        "ChannelMessage.Send",
        "ChannelMessage.Read.All",
        "Chat.ReadWrite",
        "ChatMessage.Send",
        "Presence.Read",
        "Presence.Read.All",
        # OneDrive
        "Files.Read",
        "Files.ReadWrite",
        "Files.ReadWrite.All",
        # To Do
        "Tasks.Read",
        "Tasks.ReadWrite",
        # OneNote
        "Notes.Read",
        "Notes.ReadWrite",
        "Sites.Read.All",
    ]

    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(self.required_scopes),
            "state": state,
            "prompt": "select_account",  # Forces account picker for multi-account clarity
        }
        return f"{self.auth_url_template}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> TokenResponse:
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.required_scopes),
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            self.token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            logger.error("Microsoft token exchange failed (HTTP)", status=exc.code, body=error_body)
            raise ValueError(f"Microsoft OAuth token exchange failed: {error_body}") from exc
        except Exception as exc:
            logger.error("Microsoft token exchange failed", error=str(exc))
            raise

        if "error" in resp_data:
            raise ValueError(f"Microsoft OAuth error: {resp_data.get('error_description', resp_data.get('error'))}")

        granted_scopes = resp_data.get("scope", "").split()

        return TokenResponse(
            access_token=resp_data["access_token"],
            refresh_token=resp_data.get("refresh_token"),
            expires_in=resp_data.get("expires_in"),
            scopes=granted_scopes if granted_scopes else self.required_scopes,
            metadata={
                "token_type": resp_data.get("token_type"),
                "ext_expires_in": resp_data.get("ext_expires_in"),
            },
        )

    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str) -> TokenResponse:
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": " ".join(self.required_scopes),
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            self.token_endpoint,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            logger.error("Microsoft token refresh failed (HTTP)", status=exc.code, body=error_body)
            raise ValueError(f"Microsoft OAuth refresh failed: {error_body}") from exc
        except Exception as exc:
            logger.error("Microsoft token refresh failed", error=str(exc))
            raise

        if "error" in resp_data:
            raise ValueError(f"Microsoft refresh error: {resp_data.get('error_description', resp_data.get('error'))}")

        granted_scopes = resp_data.get("scope", "").split()

        return TokenResponse(
            access_token=resp_data["access_token"],
            refresh_token=resp_data.get("refresh_token", refresh_token),
            expires_in=resp_data.get("expires_in"),
            scopes=granted_scopes if granted_scopes else self.required_scopes,
            metadata={},
        )

    async def revoke_token(self, token: str, client_id: str = "", client_secret: str = "") -> None:
        # Microsoft delegated tokens expire naturally.
        # Sign-out requires redirecting the user; no server-side revoke endpoint for Graph delegated tokens.
        logger.info("Microsoft token revoke requested — tokens expire naturally; no server-side revoke for delegated flow.")
