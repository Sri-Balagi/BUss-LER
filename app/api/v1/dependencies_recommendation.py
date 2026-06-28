"""Recommendation dependencies for API v1."""

from fastapi import Depends
from supabase import AsyncClient

from app.api.v1.dependencies_core import get_supabase_client, get_event_bus
from app.api.v1.dependencies_ai import get_ai_kernel
from app.api.v1.dependencies_trace import get_cognitive_trace_service
from app.api.v1.dependencies_planning import get_context_builder
from app.events.bus import EventBus
from app.services.ai.kernel import AbstractAIKernel


async def get_recommendation_repository(
    client: AsyncClient = Depends(get_supabase_client),
):
    from app.repositories.recommendation_repository import RecommendationRepository

    return RecommendationRepository(client)


async def get_recommendation_service(
    repository=Depends(get_recommendation_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.recommendation_service import RecommendationService

    return RecommendationService(repository=repository, event_bus=event_bus)


async def get_recommendation_engine(
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    repository=Depends(get_recommendation_repository),
    context_builder=Depends(get_context_builder),
    trace_service=Depends(get_cognitive_trace_service),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.recommendation_engine import RecommendationEngine

    return RecommendationEngine(
        ai_kernel=ai_kernel,
        repository=repository,
        context_builder=context_builder,
        trace_service=trace_service,
        event_bus=event_bus,
    )
