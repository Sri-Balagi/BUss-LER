"""BizOS Unified OAuth Flow Orchestrator — Phase 2 Production Grade

Handles the complete OAuth 2.0 flow for all Phase 2 connectors from a single
entry point. The orchestration layer only ever supplies a user_email; this module
resolves it to the appropriate provider auth flow.

Supported providers:
  google     — Google OAuth 2.0 (Drive + Calendar + Docs + Sheets + Gmail)
  microsoft  — Microsoft OAuth 2.0 via MSAL (OneDrive + SharePoint)
  notion     — Notion OAuth 2.0 (or integration token provisioning)

Email-only onboarding model:
  1. Caller supplies user_email + provider
  2. This module generates an authorization URL (with email as login hint)
  3. User is redirected to provider consent screen
  4. Provider calls back to /api/v1/connectors/{provider}/callback
  5. This module exchanges the code for tokens and stores in vault
  6. Returns a ConnectorSession for the caller
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from app.connectors.auth.vault import ConnectorAuthVault, AuthProviderType
from app.connectors.sdk.session import ConnectorSession, ConnectorSessionManager, ConnectorLifecycleState
from app.connectors.sdk.permissions import ConnectorPermission
from app.connectors.hubspot.connector import HubSpotConnector
from app.connectors.salesforce.connector import SalesforceConnector

logger = structlog.get_logger(__name__)

# ── Google OAuth Configuration ────────────────────────────────────────────────

GOOGLE_SCOPES = [
    # Drive — full access
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.activity.readonly",
    # Calendar — full access
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    # Docs + Sheets (Phase 2 future)
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    # Gmail — read/send/modify
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    # User info for email association
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Microsoft Graph scopes
MICROSOFT_SCOPES = [
    "offline_access",
    "openid",
    "email",
    "profile",
    "Files.ReadWrite.All",
    "Sites.ReadWrite.All",
    "Sites.Manage.All",
    "User.Read",
]

class OAuthStateStore:
    """Persistent + In-Memory OAuth state store for CSRF protection.

    Guarantees that OAuth state:
    1. Is persisted before redirecting (saved to disk and memory).
    2. Survives the entire OAuth round-trip across server restarts or dev reloads (--reload).
    3. Is removed only after successful validation in the callback.
    4. Expired states (> 30 minutes) are automatically rejected and pruned.
    """
    _STATE_FILE = Path(".bizos_oauth_states.json")
    _memory_store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _load_disk(cls) -> Dict[str, Dict[str, Any]]:
        if not cls._STATE_FILE.exists():
            return {}
        try:
            content = cls._STATE_FILE.read_text(encoding="utf-8")
            return json.loads(content) if content else {}
        except Exception:
            return {}

    @classmethod
    def _save_disk(cls, data: Dict[str, Dict[str, Any]]) -> None:
        try:
            cls._STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed to save oauth states to disk", error=str(exc))

    @classmethod
    def save_state(cls, state: str, payload: Dict[str, Any]) -> None:
        payload["_created_at"] = time.time()
        cls._memory_store[state] = payload
        disk_data = cls._load_disk()
        disk_data[state] = payload
        cls._save_disk(disk_data)
        logger.debug("Persisted OAuth state before redirect", state=state[:8] + "...")

    @classmethod
    def get_and_remove(cls, state: str) -> Optional[Dict[str, Any]]:
        payload = cls._memory_store.pop(state, None)
        disk_data = cls._load_disk()
        disk_payload = disk_data.pop(state, None)
        if disk_payload is not None:
            cls._save_disk(disk_data)
            payload = payload or disk_payload

        if payload is not None:
            created_at = payload.get("_created_at", time.time())
            if time.time() - created_at > 1800:
                logger.warning("OAuth state expired", state=state[:8] + "...")
                return None
            logger.debug("Successfully validated and removed OAuth state", state=state[:8] + "...")
            return payload
        return None


def _build_google_client_config() -> Dict[str, Any]:
    """Build Google OAuth client config from environment variables."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.environ.get(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/v1/connectors/google/callback",
    )

    if not client_id or not client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment. "
            "Create credentials at https://console.cloud.google.com/apis/credentials"
        )

    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }


# ── Main OAuth Flow Class ─────────────────────────────────────────────────────


class UnifiedOAuthFlow:
    """Unified OAuth orchestrator for Google, Microsoft, and Notion.

    Usage:
        flow = UnifiedOAuthFlow()

        # Step 1 — Generate auth URL
        result = await flow.initiate(user_email="user@example.com", provider="google")
        # Redirect user to result["auth_url"]

        # Step 2 — Handle callback
        session = await flow.handle_callback(
            provider="google", code="...", state="..."
        )
    """

    async def initiate(
        self,
        user_email: str,
        provider: str,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
        requested_scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate the authorization URL for the given provider.

        Args:
            user_email: The user's email (used as OAuth login hint).
            provider: 'google', 'microsoft', or 'notion'.
            tenant_id: BizOS tenant ID.
            account_id: Account identifier for multi-account support.
            requested_scopes: Override default scopes (optional).

        Returns:
            {"auth_url": str, "state": str, "provider": str}
        """
        provider = provider.lower()
        state = secrets.token_urlsafe(32)
        code_verifier = None

        if provider == "google":
            auth_url, code_verifier = await self._initiate_google(
                user_email=user_email,
                state=state,
                scopes=requested_scopes or GOOGLE_SCOPES,
            )
        elif provider == "microsoft":
            auth_url = await self._initiate_microsoft(
                user_email=user_email,
                state=state,
                scopes=requested_scopes or MICROSOFT_SCOPES,
            )
        elif provider == "notion":
            auth_url = await self._initiate_notion(user_email=user_email, state=state)
        elif provider == "hubspot":
            hs = HubSpotConnector()
            res = await hs.authenticate(user_email=user_email, tenant_id=tenant_id, account_id=account_id)
            auth_url = res["oauth_url"] + f"&state={state}"
        elif provider == "salesforce":
            sf = SalesforceConnector()
            res = await sf.authenticate(user_email=user_email, tenant_id=tenant_id, account_id=account_id)
            auth_url = res["oauth_url"] + f"&state={state}"
        else:
            raise ValueError(f"Unsupported OAuth provider: '{provider}'. Must be google, microsoft, notion, hubspot, or salesforce.")

        # Persist state (and PKCE code_verifier if generated) for CSRF validation and token exchange
        OAuthStateStore.save_state(state, {
            "user_email": user_email,
            "provider": provider,
            "tenant_id": tenant_id,
            "account_id": account_id,
            "code_verifier": code_verifier,
        })

        logger.info(
            "OAuth flow initiated",
            provider=provider,
            user_email=user_email,
            tenant_id=tenant_id,
        )

        return {"auth_url": auth_url, "state": state, "provider": provider}

    async def handle_callback(
        self,
        provider: str,
        code: str,
        state: str,
    ) -> Dict[str, Any]:
        """Handle OAuth callback: validate state, exchange code for tokens, store in vault.

        Returns:
            {"session": ConnectorSession.model_dump(), "user_email": str, "connected_services": [...]}
        """
        # CSRF validation: validate against persisted state and remove only after successful retrieval
        state_data = OAuthStateStore.get_and_remove(state)
        if not state_data:
            raise ValueError("Invalid or expired OAuth state. Possible CSRF attempt.")

        provider = provider.lower()
        user_email = state_data["user_email"]
        tenant_id = state_data["tenant_id"]
        account_id = state_data["account_id"]
        code_verifier = state_data.get("code_verifier")

        if provider == "google":
            result = await self._complete_google(
                code=code,
                user_email=user_email,
                tenant_id=tenant_id,
                account_id=account_id,
                code_verifier=code_verifier,
            )
        elif provider == "microsoft":
            result = await self._complete_microsoft(
                code=code,
                user_email=user_email,
                tenant_id=tenant_id,
                account_id=account_id,
            )
        elif provider == "notion":
            result = await self._complete_notion(
                code=code,
                user_email=user_email,
                tenant_id=tenant_id,
                account_id=account_id,
            )
        else:
            raise ValueError(f"Unsupported OAuth provider: '{provider}'")

        logger.info(
            "OAuth callback completed",
            provider=provider,
            user_email=user_email,
            tenant_id=tenant_id,
        )

        return result

    async def refresh_token(
        self,
        provider: str,
        user_id: str,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
    ) -> Dict[str, Any]:
        """Silently refresh an expired access token using the stored refresh token."""
        provider = provider.lower()
        stored = ConnectorAuthVault.get_tokens(provider, tenant_id=tenant_id, account_id=account_id)

        if not stored:
            raise RuntimeError(
                f"No stored credentials found for provider='{provider}' "
                f"user='{user_id}'. User must re-authenticate."
            )

        refresh_token = stored.get("refresh_token")
        if not refresh_token:
            raise RuntimeError(f"No refresh token stored for provider='{provider}'.")

        if provider == "google":
            return await self._refresh_google(
                refresh_token=refresh_token,
                tenant_id=tenant_id,
                account_id=account_id,
            )
        elif provider == "microsoft":
            return await self._refresh_microsoft(
                refresh_token=refresh_token,
                tenant_id=tenant_id,
                account_id=account_id,
            )
        else:
            raise ValueError(f"Token refresh not supported for provider: '{provider}'")

    # ── Google ────────────────────────────────────────────────────────────────

    async def _initiate_google(
        self, user_email: str, state: str, scopes: List[str]
    ) -> Tuple[str, Optional[str]]:
        redirect_uri = os.environ.get(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/google/callback",
        )
        flow = Flow.from_client_config(
            _build_google_client_config(),
            scopes=scopes,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            login_hint=user_email,
            state=state,
        )
        return auth_url, getattr(flow, "code_verifier", None)

    async def _complete_google(
        self,
        code: str,
        user_email: str,
        tenant_id: str,
        account_id: str,
        code_verifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        redirect_uri = os.environ.get(
            "GOOGLE_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/google/callback",
        )
        flow = Flow.from_client_config(
            _build_google_client_config(),
            scopes=GOOGLE_SCOPES,
            redirect_uri=redirect_uri,
        )
        if code_verifier:
            flow.code_verifier = code_verifier
        flow.fetch_token(code=code)
        credentials: Credentials = flow.credentials

        # Resolve user ID from email
        user_id = hashlib.sha256(user_email.encode()).hexdigest()[:16]

        # Store tokens in vault
        ConnectorAuthVault.set_tokens(
            provider_id="google",
            access_token=credentials.token or "",
            refresh_token=credentials.refresh_token or "",
            tenant_id=tenant_id,
            account_id=account_id,
            expires_at=credentials.expiry,
            scopes=list(credentials.scopes or GOOGLE_SCOPES),
            user_id=user_id,
            user_email=user_email,
        )

        # Create session
        session = ConnectorSessionManager.create_session(
            provider_id="google",
            tenant_id=tenant_id,
            account_id=account_id,
            permissions=[
                ConnectorPermission.READ_DRIVE,
                ConnectorPermission.WRITE_DRIVE,
                ConnectorPermission.DELETE_DRIVE,
                ConnectorPermission.READ_CALENDAR,
                ConnectorPermission.WRITE_CALENDAR,
                ConnectorPermission.EXPORT_DRIVE,
                ConnectorPermission.WATCH_DRIVE,
                ConnectorPermission.WATCH_CALENDAR,
            ],
            metadata={"user_email": user_email, "user_id": user_id},
        )

        return {
            "status": "SUCCESS",
            "provider": "google",
            "user_email": user_email,
            "user_id": user_id,
            "connected_services": ["google_drive", "google_calendar", "google_docs", "google_sheets", "google_gmail"],
            "session_id": session.session_id,
            "scopes_granted": list(credentials.scopes or GOOGLE_SCOPES),
        }

    async def _refresh_google(
        self,
        refresh_token: str,
        tenant_id: str,
        account_id: str,
    ) -> Dict[str, Any]:
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        ConnectorAuthVault.set_tokens(
            provider_id="google",
            access_token=token_data["access_token"],
            refresh_token=refresh_token,
            tenant_id=tenant_id,
            account_id=account_id,
            expires_in=token_data.get("expires_in", 3600),
        )

        return {"status": "REFRESHED", "provider": "google", "expires_in": token_data.get("expires_in")}

    # ── Microsoft ─────────────────────────────────────────────────────────────

    async def _initiate_microsoft(
        self, user_email: str, state: str, scopes: List[str]
    ) -> str:
        client_id = os.environ.get("MICROSOFT_CLIENT_ID", "")
        tenant_id = os.environ.get("MICROSOFT_TENANT_ID", "common")
        redirect_uri = os.environ.get(
            "MICROSOFT_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/microsoft/callback",
        )

        if not client_id:
            raise RuntimeError("MICROSOFT_CLIENT_ID must be set. Register an app at https://portal.azure.com")

        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(scopes),
            "state": state,
            "login_hint": user_email,
            "prompt": "consent",
        }
        base = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        return f"{base}?{urllib.parse.urlencode(params)}"

    async def _complete_microsoft(
        self,
        code: str,
        user_email: str,
        tenant_id: str,
        account_id: str,
    ) -> Dict[str, Any]:
        client_id = os.environ.get("MICROSOFT_CLIENT_ID", "")
        client_secret = os.environ.get("MICROSOFT_CLIENT_SECRET", "")
        ms_tenant = os.environ.get("MICROSOFT_TENANT_ID", "common")
        redirect_uri = os.environ.get(
            "MICROSOFT_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/microsoft/callback",
        )

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{ms_tenant}/oauth2/v2.0/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": " ".join(MICROSOFT_SCOPES),
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        user_id = hashlib.sha256(user_email.encode()).hexdigest()[:16]

        ConnectorAuthVault.set_tokens(
            provider_id="microsoft",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            tenant_id=tenant_id,
            account_id=account_id,
            expires_in=token_data.get("expires_in", 3600),
            scopes=MICROSOFT_SCOPES,
            user_id=user_id,
            user_email=user_email,
        )

        session = ConnectorSessionManager.create_session(
            provider_id="microsoft",
            tenant_id=tenant_id,
            account_id=account_id,
            permissions=[
                ConnectorPermission.READ_ONEDRIVE,
                ConnectorPermission.WRITE_ONEDRIVE,
                ConnectorPermission.READ_SHAREPOINT,
                ConnectorPermission.WRITE_SHAREPOINT,
            ],
            metadata={"user_email": user_email, "user_id": user_id},
        )

        return {
            "status": "SUCCESS",
            "provider": "microsoft",
            "user_email": user_email,
            "user_id": user_id,
            "connected_services": ["onedrive", "sharepoint"],
            "session_id": session.session_id,
        }

    async def _refresh_microsoft(
        self,
        refresh_token: str,
        tenant_id: str,
        account_id: str,
    ) -> Dict[str, Any]:
        client_id = os.environ.get("MICROSOFT_CLIENT_ID", "")
        client_secret = os.environ.get("MICROSOFT_CLIENT_SECRET", "")
        ms_tenant = os.environ.get("MICROSOFT_TENANT_ID", "common")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://login.microsoftonline.com/{ms_tenant}/oauth2/v2.0/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": " ".join(MICROSOFT_SCOPES),
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        ConnectorAuthVault.set_tokens(
            provider_id="microsoft",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", refresh_token),
            tenant_id=tenant_id,
            account_id=account_id,
            expires_in=token_data.get("expires_in", 3600),
        )

        return {"status": "REFRESHED", "provider": "microsoft", "expires_in": token_data.get("expires_in")}

    # ── Notion ────────────────────────────────────────────────────────────────

    async def _initiate_notion(self, user_email: str, state: str) -> str:
        notion_client_id = os.environ.get("NOTION_OAUTH_CLIENT_ID", "")
        redirect_uri = os.environ.get(
            "NOTION_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/notion/callback",
        )

        if notion_client_id:
            # Full Notion OAuth 2.0 flow
            params = {
                "client_id": notion_client_id,
                "response_type": "code",
                "owner": "user",
                "redirect_uri": redirect_uri,
                "state": state,
            }
            return f"https://api.notion.com/v1/oauth/authorize?{urllib.parse.urlencode(params)}"
        else:
            # Fallback: BizOS integration token mode — direct API token provisioning
            # Return a BizOS-specific "paste your token" UI URL
            return f"http://localhost:8000/api/v1/connectors/notion/provision?email={urllib.parse.quote(user_email)}&state={state}"

    async def _complete_notion(
        self,
        code: str,
        user_email: str,
        tenant_id: str,
        account_id: str,
    ) -> Dict[str, Any]:
        notion_client_id = os.environ.get("NOTION_OAUTH_CLIENT_ID", "")
        notion_client_secret = os.environ.get("NOTION_OAUTH_CLIENT_SECRET", "")
        redirect_uri = os.environ.get(
            "NOTION_REDIRECT_URI",
            "http://localhost:8000/api/v1/connectors/notion/callback",
        )

        import base64
        credentials = base64.b64encode(f"{notion_client_id}:{notion_client_secret}".encode()).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.notion.com/v1/oauth/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/json",
                },
                json={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
            )
            resp.raise_for_status()
            token_data = resp.json()

        user_id = hashlib.sha256(user_email.encode()).hexdigest()[:16]

        ConnectorAuthVault.set_tokens(
            provider_id="notion",
            access_token=token_data["access_token"],
            refresh_token="",  # Notion tokens don't expire
            tenant_id=tenant_id,
            account_id=account_id,
            scopes=["read", "write"],
            user_id=user_id,
            user_email=user_email,
            extra={
                "workspace_id": token_data.get("workspace_id"),
                "workspace_name": token_data.get("workspace_name"),
                "workspace_icon": token_data.get("workspace_icon"),
                "bot_id": token_data.get("bot_id"),
            },
        )

        session = ConnectorSessionManager.create_session(
            provider_id="notion",
            tenant_id=tenant_id,
            account_id=account_id,
            permissions=[ConnectorPermission.READ_NOTION, ConnectorPermission.WRITE_NOTION],
            metadata={"user_email": user_email, "workspace_id": token_data.get("workspace_id")},
        )

        return {
            "status": "SUCCESS",
            "provider": "notion",
            "user_email": user_email,
            "workspace_name": token_data.get("workspace_name"),
            "session_id": session.session_id,
        }
