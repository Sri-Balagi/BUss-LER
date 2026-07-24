
from app.application.system.query_service import SystemQueryService
from app.bootstrap.container import get_container


async def get_system_query_service() -> SystemQueryService:
    return get_container().resolve(SystemQueryService)
