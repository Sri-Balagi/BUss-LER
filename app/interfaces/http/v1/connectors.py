"""BizOS Connector Management & Capability Discovery HTTP API Router"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel

from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry
from app.connectors.sdk.session import ConnectorSessionManager
from app.connectors.runtime.bridge import UniversalConnectorRuntimeBridge
from app.connectors.runtime.analytics import ConnectorAnalyticsTracker
from app.connectors.webhooks.framework import WebhookReceiver
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode

router = APIRouter(prefix="/connectors", tags=["Connectors"])


class ExecuteConnectorRequest(BaseModel):
    capability_or_connector_id: str
    action: str
    params: Dict[str, Any] = {}
    execution_mode: ExecutionMode = ExecutionMode.PRODUCTION
    session_id: Optional[str] = None


@router.get("", summary="List all registered connectors and metadata")
async def list_connectors():
    """Returns metadata for all registered connectors in the system."""
    return {"connectors": ConnectorCapabilityRegistry.list_all_connectors()}


@router.get("/capabilities", summary="Capability Discovery API")
async def list_capabilities():
    """GET /api/v1/capabilities - Returns mapping of capabilities to implementing connectors."""
    return {
        "capabilities": ConnectorCapabilityRegistry.list_all_capabilities()
    }


@router.get("/{connector_id}/manifest", summary="Get connector manifest")
async def get_connector_manifest(connector_id: str):
    """Retrieves the static manifest for a given connector."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
    return connector.get_metadata()


@router.get("/{connector_id}/health", summary="Get rich connector health report")
async def get_connector_health(connector_id: str):
    """Retrieves rich health report for a connector."""
    connector = ConnectorCapabilityRegistry.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
    return await connector.health_check()


@router.get("/{connector_id}/analytics", summary="Get connector real-time analytics")
async def get_connector_analytics(connector_id: str):
    """Retrieves real-time execution analytics and metrics."""
    return ConnectorAnalyticsTracker.get_connector_stats(connector_id)


@router.post("/execute", summary="Execute connector action via Capability Registry")
async def execute_action(req: ExecuteConnectorRequest):
    """Executes a connector action dynamically resolved via Capability Registry."""
    connector = ConnectorCapabilityRegistry.resolve_primary_connector(req.capability_or_connector_id)
    if not connector:
        connector = ConnectorCapabilityRegistry.get_connector(req.capability_or_connector_id)
    if not connector:
        raise HTTPException(
            status_code=404,
            detail=f"No connector or capability matching '{req.capability_or_connector_id}' found",
        )

    context = ExecutionContext(
        tenant_id="default_tenant",
        execution_mode=req.execution_mode,
        principal_id="api_user",
    )
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/webhooks/{provider_id}", summary="Generic Webhook Ingestion Endpoint")
async def receive_webhook(provider_id: str, request: Request):
    """Receives and validates webhooks for Stripe, Razorpay, Google Workspace, etc."""
    body_bytes = await request.body()
    headers = dict(request.headers)
    try:
        event = WebhookReceiver.process_webhook(provider_id, body_bytes, headers)
        return {"status": "RECEIVED", "event_id": event.event_id, "event_type": event.event_type}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
