import asyncio
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from app.models.enterprise_context import EnterpriseContext
from app.models.enums import ContextStatus
from app.models.events import ContextInvalidatedEvent
from app.services.context_cache import (
    MemoryContextCache,
    RedisContextCache,
    build_cache_key,
)
from app.services.context_freshness import ContextFreshnessPolicy


@pytest.fixture
def cache():
    return MemoryContextCache()


@pytest.fixture
def mock_context():
    context = MagicMock(spec=EnterpriseContext)
    context.status = ContextStatus.ASSEMBLED
    context.id = uuid4()
    context.twin_id = uuid4()
    return context


@pytest.fixture
def mock_freshness_policy():
    policy = MagicMock(spec=ContextFreshnessPolicy)
    policy.is_stale.return_value = False
    return policy


@pytest.mark.asyncio
async def test_get_set(cache, mock_context):
    key = "test_key"
    await cache.set(key, mock_context, 60)

    retrieved = await cache.get(key)
    assert retrieved == mock_context
    assert cache.size() == 1
    assert cache.health()["entries"] == 1


@pytest.mark.asyncio
async def test_get_expired(cache, mock_context):
    key = "test_key_expired"
    # Set with 0 TTL
    await cache.set(key, mock_context, 0)

    # Sleep slightly to ensure expiration
    await asyncio.sleep(0.01)

    retrieved = await cache.get(key)
    assert retrieved is None
    assert cache.size() == 0


@pytest.mark.asyncio
async def test_invalidate_no_event_bus(cache, mock_context):
    key = "test_key"
    await cache.set(key, mock_context, 60)

    await cache.invalidate(key, mock_context.twin_id)

    retrieved = await cache.get(key)
    assert retrieved is None
    assert cache.size() == 0


@pytest.mark.asyncio
async def test_invalidate_with_event_bus(cache, mock_context):
    key = "test_key"
    await cache.set(key, mock_context, 60)

    mock_bus = MagicMock()
    await cache.invalidate(key, mock_context.twin_id, event_bus=mock_bus)

    retrieved = await cache.get(key)
    assert retrieved is None

    mock_bus.publish.assert_called_once()
    event = mock_bus.publish.call_args[0][0]
    assert isinstance(event, ContextInvalidatedEvent)
    assert event.cache_key == key


@pytest.mark.asyncio
async def test_is_fresh(cache, mock_context, mock_freshness_policy):
    key = "test_key"

    # Not in cache
    assert await cache.is_fresh(key, mock_freshness_policy) is False

    # In cache, policy says fresh
    await cache.set(key, mock_context, 60)
    assert await cache.is_fresh(key, mock_freshness_policy) is True

    # In cache, policy says stale
    mock_freshness_policy.is_stale.return_value = True
    assert await cache.is_fresh(key, mock_freshness_policy) is False


@pytest.mark.asyncio
async def test_redis_raises(mock_context, mock_freshness_policy):
    redis_cache = RedisContextCache()
    key = "test_key"

    with pytest.raises(NotImplementedError):
        await redis_cache.get(key)

    with pytest.raises(NotImplementedError):
        await redis_cache.set(key, mock_context, 60)

    with pytest.raises(NotImplementedError):
        await redis_cache.invalidate(key, mock_context.twin_id)

    with pytest.raises(NotImplementedError):
        await redis_cache.is_fresh(key, mock_freshness_policy)


def test_build_cache_key():
    twin_id = uuid4()
    policy_id = "test_policy"

    key_no_intent = build_cache_key(twin_id, policy_id)
    assert key_no_intent == f"{twin_id}:{policy_id}:no_intent"

    intent_id = uuid4()
    key_with_intent = build_cache_key(twin_id, policy_id, intent_id)
    assert key_with_intent == f"{twin_id}:{policy_id}:{intent_id}"
