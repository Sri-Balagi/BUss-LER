"""Planning dependencies for API v1."""

from fastapi import Depends
from app.bootstrap.container import get_container

async def get_plan_repository():
    from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository
    return get_container().resolve(PlanRepository)

async def get_plan_service():
    from app.application.planning.plan_service import PlanService
    return get_container().resolve(PlanService)

async def get_context_builder():
    from app.application.planning.context_builder import ContextBuilder
    return get_container().resolve(ContextBuilder)

async def get_planning_engine():
    from app.application.planning.planning_engine import PlanningEngine
    return get_container().resolve(PlanningEngine)
