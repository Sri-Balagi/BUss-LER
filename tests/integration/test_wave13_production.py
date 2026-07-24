import asyncio

import pytest

from app.infrastructure.cache.manager import CacheManager
from app.infrastructure.dr.manager import DisasterRecoveryManager, IBackupProvider
from app.infrastructure.monitoring.observability import MetricsRegistry, Tracer
from app.infrastructure.providers.interfaces import IMessageQueue, IRedisProvider
from app.infrastructure.workers.worker import DistributedWorker


class MockRedisProvider(IRedisProvider):
    def __init__(self):
        self.store = {}
    async def get(self, key): return self.store.get(key)
    async def set(self, key, value, ttl=None): self.store[key] = value
    async def delete(self, key): self.store.pop(key, None)

class MockMessageQueue(IMessageQueue):
    def __init__(self):
        self.q = []
        self.acked = []
    async def push(self, queue, msg): self.q.append(msg)
    async def pop(self, queue, timeout=0): return self.q.pop(0) if self.q else None
    async def ack(self, msg_id): self.acked.append(msg_id)
    async def nack(self, msg_id): pass
    async def heartbeat(self, worker_id, ts): pass

class MockBackup(IBackupProvider):
    async def create_snapshot(self, id): return "snap-123"
    async def restore_snapshot(self, id, snap): pass

@pytest.mark.asyncio
async def test_cache_manager():
    redis = MockRedisProvider()
    cache = CacheManager(redis)
    await cache.set("k1", {"foo": "bar"})
    val = await cache.get("k1")
    assert val["foo"] == "bar"
    await cache.invalidate("k1")
    assert await cache.get("k1") is None
    stats = cache.get_statistics()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["invalidations"] == 1

@pytest.mark.asyncio
async def test_distributed_worker():
    mq = MockMessageQueue()
    worker = DistributedWorker("task_q", mq)

    processed = False
    async def handler(msg):
        nonlocal processed
        processed = True

    worker.register_handler("TEST_TASK", handler)

    await mq.push("task_q", {"id": "1", "type": "TEST_TASK"})
    msg = await mq.pop("task_q")
    await worker._process_message(msg)

    assert processed is True
    assert "1" in mq.acked

@pytest.mark.asyncio
async def test_dr_manager():
    provider = MockBackup()
    dr = DisasterRecoveryManager(provider)
    snap = await dr.backup_repository("main_db")
    assert snap == "snap-123"
    await dr.restore_repository("main_db", snap)

def test_monitoring():
    registry = MetricsRegistry()
    registry.inc("http_requests", 1, {"method": "GET"})
    output = registry.export_prometheus()
    assert 'http_requests{method="GET"} 1' in output

    tracer = Tracer()
    ctx = tracer.start_span("test")
    assert ctx.trace_id is not None
    tracer.end_span(ctx)
