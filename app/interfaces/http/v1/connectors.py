"""BizOS Connector Management, Capability Discovery & OAuth Lifecycle HTTP API Router

Endpoints:
  Auth:
    POST /connectors/{provider}/authenticate  — initiate OAuth for user email
    GET  /connectors/google/callback          — Google OAuth callback (registered redirect URI)
    GET  /connectors/microsoft/callback       — Microsoft OAuth callback
    GET  /connectors/notion/callback          — Notion OAuth callback
    POST /connectors/{provider}/disconnect    — revoke tokens

  Discovery:
    GET  /connectors                          — list all registered connectors
    GET  /connectors/capabilities             — capability → connector mapping
    GET  /connectors/{connector_id}/health    — connector health report
    GET  /connectors/{connector_id}/manifest  — machine-readable manifest
    GET  /connectors/{connector_id}/analytics — real-time analytics

  Execution:
    POST /connectors/execute                  — execute via capability registry
    POST /connectors/{connector_id}/execute   — execute on specific connector
    POST /connectors/{connector_id}/sync      — trigger delta sync
    POST /connectors/{connector_id}/watch     — subscribe to webhooks

  Webhooks:
    POST /connectors/webhooks/{provider_id}   — generic webhook ingestion
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.connectors.auth.oauth_flow import UnifiedOAuthFlow
from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry
from app.connectors.sdk.session import ConnectorSessionManager
from app.connectors.runtime.bridge import UniversalConnectorRuntimeBridge
from app.connectors.runtime.analytics import ConnectorAnalyticsTracker
from app.connectors.webhooks.framework import WebhookReceiver
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


def _make_context(
    tenant_id: str = "default_tenant",
    principal_id: str = "api_user",
    execution_mode: Any = None,
) -> ExecutionContext:
    """Create a valid ExecutionContext for connector router calls."""
    trace_id = str(uuid.uuid4())
    return ExecutionContext(
        tenant_id=tenant_id,
        principal_id=principal_id,
        session_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        trace_id=trace_id,
        correlation_id=trace_id,
        execution_mode=execution_mode,
    )

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/connectors", tags=["Connectors"])
_oauth_flow = UnifiedOAuthFlow()


# ── Request Schemas ───────────────────────────────────────────────────────────


class AuthenticateRequest(BaseModel):
    """Email-only onboarding: user provides email, BizOS handles the rest."""
    user_email: str
    tenant_id: str = "default_tenant"
    account_id: str = "default"


class DisconnectRequest(BaseModel):
    user_id: str
    tenant_id: str = "default_tenant"
    account_id: str = "default"


class ExecuteConnectorRequest(BaseModel):
    capability_or_connector_id: str
    action: str
    params: Dict[str, Any] = {}
    execution_mode: ExecutionMode = ExecutionMode.PRODUCTION
    session_id: Optional[str] = None


class ExecuteOnConnectorRequest(BaseModel):
    capability: str
    params: Dict[str, Any] = {}
    execution_mode: ExecutionMode = ExecutionMode.PRODUCTION
    account_id: str = "default"
    page_size: int = 100
    page_token: Optional[str] = None


class WatchRequest(BaseModel):
    resource_type: str = "file"
    resource_id: Optional[str] = None
    webhook_url: str


class SyncRequest(BaseModel):
    resource_type: str = "file"
    sync_token: Optional[str] = None


# ── Discovery Endpoints ───────────────────────────────────────────────────────


@router.get("", summary="List all registered connectors")
async def list_connectors():
    """Returns metadata for all registered connectors."""
    return {"connectors": ConnectorCapabilityRegistry.list_all_connectors()}


@router.get("/capabilities", summary="Capability Discovery API")
async def list_capabilities():
    """Returns mapping of capabilities to implementing connectors."""
    return {"capabilities": ConnectorCapabilityRegistry.list_all_capabilities()}


@router.get("/{connector_id}/manifest", summary="Get connector machine-readable manifest")
async def get_connector_manifest(connector_id: str):
    """Returns the full machine-readable manifest for a connector."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")

    # Try to load from manifest.json file first (richer data)
    if hasattr(connector, "_load_manifest"):
        return connector._load_manifest()
    return connector.get_metadata()


@router.get("/{connector_id}/health", summary="Get connector health report")
async def get_connector_health(connector_id: str):
    """Returns a rich health report for a connector."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
    return await connector.health()


@router.get("/{connector_id}/analytics", summary="Get connector real-time analytics")
async def get_connector_analytics(connector_id: str):
    """Returns real-time execution analytics and metrics."""
    return ConnectorAnalyticsTracker.get_connector_stats(connector_id)


# ── OAuth Auth Endpoints ──────────────────────────────────────────────────────


@router.post("/{provider}/authenticate", summary="Initiate OAuth flow for user email")
async def initiate_auth(provider: str, req: AuthenticateRequest):
    """Initiate OAuth consent flow for a provider.

    The user provides only their email. BizOS generates the authorization URL
    with the email as a login hint. The user visits this URL to grant consent.

    Supported providers: google, microsoft, notion, hubspot, salesforce
    """
    try:
        result = await _oauth_flow.initiate(
            user_email=req.user_email,
            provider=provider,
            tenant_id=req.tenant_id,
            account_id=req.account_id,
        )
        return {
            "status": "PENDING_CONSENT",
            "provider": provider,
            "user_email": req.user_email,
            "auth_url": result["auth_url"],
            "state": result["state"],
            "instructions": f"Redirect the user to auth_url to complete {provider} OAuth consent.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/google/callback", summary="Google OAuth 2.0 callback endpoint", include_in_schema=True)
async def google_oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None, description="Error from Google if user denied consent"),
    scope: Optional[str] = Query(None, description="Granted scopes"),
):
    """Handle Google OAuth 2.0 callback.

    This is the registered redirect URI:
      http://localhost:8000/api/v1/connectors/google/callback

    Google redirects here after the user grants or denies consent.
    Exchanges the authorization code for access + refresh tokens.
    """
    if error:
        logger.warning("Google OAuth consent denied", error=error)
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth consent was denied or failed: {error}",
        )

    try:
        result = await _oauth_flow.handle_callback(
            provider="google", code=code, state=state
        )
        logger.info("Google OAuth completed", user_email=result.get("user_email"))
        return {
            "status": "AUTHENTICATED",
            "provider": "google",
            "user_email": result.get("user_email"),
            "connected_services": result.get("connected_services", []),
            "session_id": result.get("session_id"),
            "message": "Google authentication successful. Drive, Calendar, Docs, Sheets, and Gmail are now connected.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Google OAuth callback failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@router.get("/microsoft/callback", summary="Microsoft OAuth 2.0 callback endpoint")
async def microsoft_oauth_callback(
    code: str = Query(..., description="Authorization code from Microsoft"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle Microsoft OAuth 2.0 callback for OneDrive + SharePoint."""
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Microsoft OAuth failed: {error} — {error_description}",
        )
    try:
        result = await _oauth_flow.handle_callback(
            provider="microsoft", code=code, state=state
        )
        return {
            "status": "AUTHENTICATED",
            "provider": "microsoft",
            "user_email": result.get("user_email"),
            "connected_services": result.get("connected_services", []),
            "session_id": result.get("session_id"),
            "message": "Microsoft authentication successful. OneDrive and SharePoint are now connected.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@router.get("/notion/callback", summary="Notion OAuth 2.0 callback endpoint")
async def notion_oauth_callback(
    code: str = Query(..., description="Authorization code from Notion"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None),
):
    """Handle Notion OAuth 2.0 callback."""
    if error:
        raise HTTPException(status_code=400, detail=f"Notion OAuth failed: {error}")
    try:
        result = await _oauth_flow.handle_callback(
            provider="notion", code=code, state=state
        )
        return {
            "status": "AUTHENTICATED",
            "provider": "notion",
            "workspace_name": result.get("workspace_name"),
            "session_id": result.get("session_id"),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")




@router.get("/hubspot/callback", summary="HubSpot OAuth 2.0 callback endpoint")
async def hubspot_oauth_callback(
    code: str = Query(..., description="Authorization code from HubSpot"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle HubSpot OAuth 2.0 callback."""
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"HubSpot OAuth failed: {error} — {error_description or ''}",
        )
    try:
        result = await _oauth_flow.handle_callback(
            provider="hubspot", code=code, state=state
        )
        return HTMLResponse(content="""
        <html>
            <head><title>HubSpot Connected</title></head>
            <body style="font-family: system-ui, sans-serif; text-align: center; padding-top: 50px; background: #0f172a; color: #f8fafc;">
                <div style="max-width: 500px; margin: 0 auto; padding: 40px; border-radius: 12px; background: #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <div style="font-size: 48px; margin-bottom: 16px;">🧡</div>
                    <h1 style="color: #ff7a59; margin-bottom: 8px;">HubSpot CRM Connected!</h1>
                    <p style="color: #94a3b8; line-height: 1.5;">BizOS Universal Perception Layer is now actively observing your HubSpot CRM.</p>
                    <p style="color: #64748b; font-size: 14px; margin-top: 24px;">This window will close automatically in 3 seconds...</p>
                </div>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
        </html>
        """)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("HubSpot OAuth callback failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@router.get("/salesforce/callback", summary="Salesforce OAuth 2.0 callback endpoint")
async def salesforce_oauth_callback(
    code: str = Query(..., description="Authorization code from Salesforce"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
):
    """Handle Salesforce OAuth 2.0 callback."""
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Salesforce OAuth failed: {error} — {error_description or ''}",
        )
    try:
        result = await _oauth_flow.handle_callback(
            provider="salesforce", code=code, state=state
        )
        return HTMLResponse(content="""
        <html>
            <head><title>Salesforce Connected</title></head>
            <body style="font-family: system-ui, sans-serif; text-align: center; padding-top: 50px; background: #0f172a; color: #f8fafc;">
                <div style="max-width: 500px; margin: 0 auto; padding: 40px; border-radius: 12px; background: #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <div style="font-size: 48px; margin-bottom: 16px;">⚡</div>
                    <h1 style="color: #00a1e0; margin-bottom: 8px;">Salesforce CRM Connected!</h1>
                    <p style="color: #94a3b8; line-height: 1.5;">BizOS Universal Perception Layer is now actively observing your Salesforce CRM.</p>
                    <p style="color: #64748b; font-size: 14px; margin-top: 24px;">This window will close automatically in 3 seconds...</p>
                </div>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
        </html>
        """)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Salesforce OAuth callback failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@router.post("/{provider}/disconnect", summary="Revoke tokens and disconnect provider")
async def disconnect_provider(provider: str, req: DisconnectRequest):
    """Revoke OAuth tokens and remove all stored credentials for a provider."""
    connector = ConnectorCapabilityRegistry.get_connector(
        f"{provider}_drive" if provider == "google" else provider
    )
    if connector and hasattr(connector, "disconnect"):
        return await connector.disconnect(
            user_id=req.user_id, tenant_id=req.tenant_id, account_id=req.account_id
        )
    # Fallback: revoke directly from vault
    revoked = ConnectorAuthVault.revoke_tokens(
        provider, tenant_id=req.tenant_id, account_id=req.account_id
    )
    return {
        "status": "DISCONNECTED" if revoked else "NOT_FOUND",
        "provider": provider,
    }


@router.get("/{provider}/status", summary="Check authentication status for a provider")
async def get_auth_status(
    provider: str,
    tenant_id: str = Query("default_tenant"),
    account_id: str = Query("default_account"),
):
    """Check if a provider has stored credentials and whether they are valid."""
    tokens = ConnectorAuthVault.get_tokens(provider, tenant_id=tenant_id, account_id=account_id)
    is_expired = ConnectorAuthVault.is_token_expired(provider, tenant_id=tenant_id, account_id=account_id)
    return {
        "provider": provider,
        "authenticated": bool(tokens),
        "token_expired": is_expired,
        "user_email": tokens.get("user_email") if tokens else None,
        "scopes": tokens.get("scopes", []) if tokens else [],
    }


# ── Execution Endpoints ───────────────────────────────────────────────────────


@router.post("/execute", summary="Execute connector action via Capability Registry")
async def execute_action(req: ExecuteConnectorRequest):
    """Execute a connector action dynamically resolved via Capability Registry."""
    connector = ConnectorCapabilityRegistry.resolve_primary_connector(req.capability_or_connector_id)
    if not connector:
        connector = ConnectorCapabilityRegistry.get_connector(req.capability_or_connector_id)
    if not connector:
        raise HTTPException(
            status_code=404,
            detail=f"No connector or capability matching '{req.capability_or_connector_id}' found",
        )

    context = _make_context(execution_mode=req.execution_mode)
    session = ConnectorSessionManager.get_session(req.session_id) if req.session_id else None

    try:
        res = await UniversalConnectorRuntimeBridge.execute(
            connector=connector,
            action=req.action,
            params=req.params,
            context=context,
            session=session,
        )
        return res
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{connector_id}/execute", summary="Execute capability on a specific connector")
async def execute_on_connector(connector_id: str, req: ExecuteOnConnectorRequest):
    """Execute a specific capability on a named connector."""
    from app.connectors.sdk.base import ConnectorExecuteRequest

    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")

    context = _make_context(execution_mode=req.execution_mode)

    try:
        execute_req = ConnectorExecuteRequest(
            capability=req.capability,
            params=req.params,
            account_id=req.account_id,
            page_size=req.page_size,
            page_token=req.page_token,
        )
        return await connector.execute(execute_req, context)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{connector_id}/sync", summary="Trigger delta sync on a connector")
async def trigger_sync(connector_id: str, req: SyncRequest):
    """Trigger a delta sync for a connector resource type."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")

    context = _make_context()

    try:
        return await connector.sync(req.resource_type, req.sync_token, context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{connector_id}/watch", summary="Subscribe to connector webhook notifications")
async def subscribe_watch(connector_id: str, req: WatchRequest):
    """Subscribe to push notifications for a connector resource."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")

    context = _make_context()

    try:
        return await connector.watch(req.resource_type, req.resource_id, req.webhook_url, context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Webhook Ingestion ─────────────────────────────────────────────────────────


@router.post("/webhooks/{provider_id}", summary="Generic Webhook Ingestion Endpoint")
async def receive_webhook(provider_id: str, request: Request):
    """Receives and validates webhooks for Google, Microsoft, Notion, etc."""
    body_bytes = await request.body()
    headers = dict(request.headers)
    try:
        event = WebhookReceiver.process_webhook(provider_id, body_bytes, headers)
        return {"status": "RECEIVED", "event_id": event.event_id, "event_type": event.event_type}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
