"""Cognitive Trace dependencies for API v1."""

from fastapi import Depends
from supabase import AsyncClient

from app.interfaces.http.v1.dependencies_core import get_event_bus, get_supabase_client
from app.shared.events.bus import EventBus


async def get_cognitive_trace_repository(
    client: AsyncClient = Depends(get_supabase_client),
):
    from app.infrastructure.persistence.postgres.repositories.cognitive_trace_repository import (
        CognitiveTraceRepository,
    )

    return CognitiveTraceRepository(client)


async def get_cognitive_trace_service(
    repository=Depends(get_cognitive_trace_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.cognitive_trace_service import CognitiveTraceService

    return CognitiveTraceService(repository=repository, event_bus=event_bus)
