import asyncio
import time

from app.infrastructure.cache.manager import CacheManager
from app.infrastructure.monitoring.observability import MetricsRegistry, Tracer


class MockRedis:
    def __init__(self):
        self.store = {}
    async def get(self, k): return self.store.get(k)
    async def set(self, k, v, t=None): self.store[k] = v
    async def delete(self, k): self.store.pop(k, None)

async def run_benchmark():
    print("Starting BizOS Benchmarks...")
    redis = MockRedis()
    cache = CacheManager(redis)
    tracer = Tracer()
    registry = MetricsRegistry()

    start_time = time.time()

    # Cache Load Test
    for i in range(10000):
        await cache.set(f"key_{i}", {"data": "test"})

    for i in range(10000):
        await cache.get(f"key_{i}")

    duration = time.time() - start_time
    print(f"Cache 10k read/write latency: {duration:.4f}s")

    # Trace Load Test
    start_time = time.time()
    for i in range(1000):
        ctx = tracer.start_span("benchmark_span")
        registry.inc("span_created")
        tracer.end_span(ctx)

    duration = time.time() - start_time
    print(f"Tracer 1k spans latency: {duration:.4f}s")
    print("Benchmarks completed.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
