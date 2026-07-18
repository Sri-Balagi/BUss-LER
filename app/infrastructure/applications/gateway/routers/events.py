from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from typing import Optional
from app.bootstrap.container import get_container
from app.application.notifications.broker import NotificationBroker
from app.infrastructure.notifications.sse_adapter import SSEAdapter
import asyncio
import json

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/stream")
async def stream_events(
    request: Request,
    session_id: Optional[str] = None,
    job_id: Optional[str] = None,
    application_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
):
    """
    Stream platform events using Server-Sent Events (SSE).
    Allows filtering by session_id, job_id, application_id, or tenant_id.
    """
    container = get_container()
    
    # We retrieve the SSE adapter from the container. 
    # The broker pushes events to this adapter.
    sse_adapter = container.resolve(SSEAdapter)
    
    queue = sse_adapter.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                # Wait for an event from the adapter
                event_dict = await queue.get()
                
                # Apply filtering
                if session_id and event_dict.get("session_id") != session_id:
                    continue
                if job_id and event_dict.get("job_id") != job_id:
                    continue
                if tenant_id and event_dict.get("tenant_id") != tenant_id:
                    continue
                # If there's an application_id filter, we might check target_app_id or similar fields
                if application_id and event_dict.get("target_app_id") != application_id:
                    continue
                
                yield json.dumps(event_dict)
        finally:
            sse_adapter.unsubscribe(queue)

    return EventSourceResponse(event_generator())
