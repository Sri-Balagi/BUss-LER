from fastapi import Depends

from app.bootstrap.container import get_container
from app.application.system.query_service import SystemQueryService


async def get_system_query_service() -> SystemQueryService:
    return get_container().resolve(SystemQueryService)
