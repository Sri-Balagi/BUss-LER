"""FastAPI Router for inbound webhooks."""
from __future__ import annotations
import logging
from typing import Any
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.connectors.exceptions.errors import WebhookError, WebhookSignatureError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["connectors-webhooks"])

# Injected at app startup
_connector_manager: Any = None


def set_webhook_connector_manager(manager: Any) -> None:
    global _connector_manager
    _connector_manager = manager


@router.post("/{connector_id}")
@router.post("/{connector_id}/{profile_id}")
async def receive_webhook(
    connector_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    profile_id: str = "default",
) -> dict[str, Any]:
    """Inbound webhook receiver endpoint."""
    if _connector_manager is None:
        raise HTTPException(status_code=503, detail="ConnectorManager not initialized")

    try:
        payload = await request.json()
    except Exception as e:
        logger.error("Invalid JSON body for webhook connector=%s: %s", connector_id, e)
        raise HTTPException(status_code=400, detail="Invalid JSON body") from e

    try:
        result = await _connector_manager.handle_webhook(
            connector_id=connector_id,
            payload=payload,
            profile_id=profile_id,
        )
        return {"status": "accepted", "connector_id": connector_id, "processed": getattr(result, "processed", True)}
    except WebhookSignatureError as e:
        logger.warning("Webhook signature verification failed for %s: %s", connector_id, e)
        raise HTTPException(status_code=401, detail="Invalid signature") from e
    except WebhookError as e:
        logger.error("Webhook processing error for %s: %s", connector_id, e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Unexpected error processing webhook for %s", connector_id)
        raise HTTPException(status_code=500, detail="Internal server error") from e
