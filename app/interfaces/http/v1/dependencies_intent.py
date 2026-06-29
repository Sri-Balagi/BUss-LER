"""Intent and Goal dependencies for API v1."""

from fastapi import Depends
from supabase import AsyncClient

from app.interfaces.http.v1.dependencies_core import get_supabase_client, get_event_bus
from app.interfaces.http.v1.dependencies_ai import get_ai_kernel
from app.interfaces.http.v1.dependencies_trace import get_cognitive_trace_service
from app.shared.events.bus import EventBus
from app.infrastructure.ai.kernel import AbstractAIKernel


async def get_intent_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.intent_repository import IntentRepository

    return IntentRepository(client)


async def get_goal_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.goal_repository import GoalRepository

    return GoalRepository(client)


async def get_goal_service(
    repository=Depends(get_goal_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.goal_service import GoalService

    return GoalService(repository=repository, event_bus=event_bus)


async def get_intent_classifier(
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    trace_service=Depends(get_cognitive_trace_service),
):
    from app.services.intent_classifier import IntentClassifier

    return IntentClassifier(ai_kernel=ai_kernel, trace_service=trace_service)


async def get_intent_service(
    repository=Depends(get_intent_repository),
    event_bus: EventBus = Depends(get_event_bus),
    classifier=Depends(get_intent_classifier),
):
    from app.services.intent_service import IntentService

    return IntentService(
        repository=repository, event_bus=event_bus, classifier=classifier
    )
