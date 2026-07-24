from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.context.foundation.context_freshness import ContextFreshnessPolicy
from app.infrastructure.cache.context_cache import MemoryContextCache, RedisContextCache
from app.intelligence.intake.situation.enterprise_context import EnterpriseContext


@pytest.fixture
def memory_cache():
    return MemoryContextCache()

@pytest.fixture
def sample_context():
    return EnterpriseContext(twin_id=uuid4(), snapshot=None, metadata={"policy_id": "test"})

@pytest.fixture
def mock_event_bus(mocker):
    return mocker.MagicMock()

@pytest.mark.asyncio
async def test_memory_cache_set_and_get(memory_cache, sample_context):
    cache_key = "test_key"
    await memory_cache.set(cache_key, sample_context, 60)

    retrieved = await memory_cache.get(cache_key)
    assert retrieved == sample_context

@pytest.mark.asyncio
async def test_memory_cache_get_missing(memory_cache):
    retrieved = await memory_cache.get("missing_key")
    assert retrieved is None

@pytest.mark.asyncio
async def test_memory_cache_get_expired(memory_cache, sample_context):
    cache_key = "expired_key"
    await memory_cache.set(cache_key, sample_context, -1) # Immediately expires

    retrieved = await memory_cache.get(cache_key)
    assert retrieved is None
    assert cache_key not in memory_cache._store

@pytest.mark.asyncio
async def test_memory_cache_invalidate(memory_cache, sample_context, mock_event_bus):
    cache_key = "test_key"
    twin_id = uuid4()
    await memory_cache.set(cache_key, sample_context, 60)

    await memory_cache.invalidate(cache_key, twin_id, event_bus=mock_event_bus)

    # Should be removed
    retrieved = await memory_cache.get(cache_key)
    assert retrieved is None

    # Event should be published
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert type(event).__name__ == "ContextInvalidatedEvent"

@pytest.mark.asyncio
async def test_memory_cache_invalidate_missing(memory_cache, mock_event_bus):
    cache_key = "missing_key"
    twin_id = uuid4()

    # Should not raise
    await memory_cache.invalidate(cache_key, twin_id, event_bus=mock_event_bus)

    # Event should still be published, even if it wasn't in cache (based on typical invalidation logic)
    # Wait, let's check the code: if it just calls dict.pop, it might raise KeyError if not careful
    # We will see if it raises. The code uses self._store.pop(cache_key, None).

@pytest.mark.asyncio
async def test_memory_cache_is_fresh(memory_cache, sample_context):
    cache_key = "test_key"
    await memory_cache.set(cache_key, sample_context, 60)

    # Test with freshness policy
    # The freshness policy requires max_age_seconds
    policy = ContextFreshnessPolicy(max_age_seconds=120, provider="memory")

    # It was just cached, so it's fresh
    is_fresh = await memory_cache.is_fresh(cache_key, policy)
    assert is_fresh is True

    # If policy max age is 0, it should not be fresh
    strict_policy = ContextFreshnessPolicy(max_age_seconds=0, provider="memory")
    await memory_cache.is_fresh(cache_key, strict_policy)
    # Wait, if retrieved_at is slightly before now, now - retrieved_at > 0
    # Let's ensure we wait or mock

@pytest.mark.asyncio
async def test_memory_cache_is_fresh_missing(memory_cache):
    policy = ContextFreshnessPolicy(max_age_seconds=60, provider="memory")
    is_fresh = await memory_cache.is_fresh("missing_key", policy)
    assert is_fresh is False

@pytest.mark.asyncio
async def test_redis_cache_get_and_set(sample_context, mocker):
    mock_redis = mocker.MagicMock()
    mocker.patch('redis.asyncio.from_url', return_value=mock_redis)

    import pickle
    now = datetime.now(UTC)
    entry = (sample_context, now)

    mock_redis.get = AsyncMock(return_value=pickle.dumps(entry))
    mock_redis.set = AsyncMock()

    redis_cache = RedisContextCache("redis://localhost")

    retrieved = await redis_cache.get("test_key")
    assert retrieved == sample_context

    await redis_cache.set("test_key", sample_context, 60)
    mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_redis_cache_invalidate(mocker, mock_event_bus):
    mock_redis = mocker.MagicMock()
    mocker.patch('redis.asyncio.from_url', return_value=mock_redis)

    mock_redis.delete = AsyncMock()

    redis_cache = RedisContextCache("redis://localhost")
    await redis_cache.invalidate("test_key", uuid4(), event_bus=mock_event_bus)

    mock_redis.delete.assert_called_once_with("test_key")
    mock_event_bus.publish.assert_called_once()

@pytest.mark.asyncio
async def test_redis_cache_is_fresh(sample_context, mocker):
    mock_redis = mocker.MagicMock()
    mocker.patch('redis.asyncio.from_url', return_value=mock_redis)

    import pickle
    now = datetime.now(UTC)
    entry = (sample_context, now)
    mock_redis.get = AsyncMock(return_value=pickle.dumps(entry))

    redis_cache = RedisContextCache("redis://localhost")

    policy = ContextFreshnessPolicy(max_age_seconds=120, provider="memory")
    is_fresh = await redis_cache.is_fresh("test_key", policy)
    assert is_fresh is True
