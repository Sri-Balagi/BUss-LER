from typing import Optional, Dict

from app.domain.identity.api_key import APIKey
from app.domain.identity.interfaces import IAPIKeyRepository


class InMemoryAPIKeyRepository(IAPIKeyRepository):
    """
    In-memory persistence for API keys.
    Used for Milestone 2 testing until PostgreSQL persistence is implemented.
    """
    
    def __init__(self):
        # Maps prefix -> APIKey
        self._store: Dict[str, APIKey] = {}
        
    async def get_by_prefix(self, prefix: str) -> Optional[APIKey]:
        return self._store.get(prefix)
        
    async def save(self, api_key: APIKey) -> None:
        self._store[api_key.prefix] = api_key
