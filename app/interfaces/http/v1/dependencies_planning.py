"""Planning dependencies for API v1."""

from fastapi import Depends
from supabase import AsyncClient

from app.interfaces.http.v1.dependencies_core import get_supabase_client, get_event_bus
from app.interfaces.http.v1.dependencies_ai import get_ai_kernel
from app.interfaces.http.v1.dependencies_trace import get_cognitive_trace_service
from app.interfaces.http.v1.dependencies_intent import get_goal_service
from app.interfaces.http.v1.dependencies_memory import get_memory_service
from app.shared.events.bus import EventBus
from app.infrastructure.ai.kernel import AbstractAIKernel


async def get_plan_repository(client: AsyncClient = Depends(get_supabase_client)):
    from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository

    return PlanRepository(client)


async def get_plan_service(
    repository=Depends(get_plan_repository),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.plan_service import PlanService

    return PlanService(repository=repository, event_bus=event_bus)


async def get_context_builder(
    goal_service=Depends(get_goal_service),
    memory_service=Depends(get_memory_service),
):
    from app.services.context_builder import ContextBuilder

    return ContextBuilder(goal_service=goal_service, memory_service=memory_service)


async def get_planning_engine(
    ai_kernel: AbstractAIKernel = Depends(get_ai_kernel),
    plan_repository=Depends(get_plan_repository),
    context_builder=Depends(get_context_builder),
    goal_service=Depends(get_goal_service),
    trace_service=Depends(get_cognitive_trace_service),
    event_bus: EventBus = Depends(get_event_bus),
):
    from app.services.planning_engine import PlanningEngine

    return PlanningEngine(
        ai_kernel=ai_kernel,
        plan_repository=plan_repository,
        context_builder=context_builder,
        goal_service=goal_service,
        trace_service=trace_service,
        event_bus=event_bus,
    )
