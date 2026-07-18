import json
from typing import Optional, Any
from app.infrastructure.providers.interfaces import IRedisProvider

class CacheManager:
    def __init__(self, redis: IRedisProvider):
        self._redis = redis
        self._stats = {"hits": 0, "misses": 0, "invalidations": 0}

    async def get(self, key: str) -> Optional[Any]:
        val = await self._redis.get(key)
        if val:
            self._stats["hits"] += 1
            return json.loads(val)
        self._stats["misses"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = 3600):
        await self._redis.set(key, json.dumps(value), ttl)

    async def invalidate(self, key: str):
        await self._redis.delete(key)
        self._stats["invalidations"] += 1

    def get_statistics(self) -> dict:
        return self._stats.copy()
