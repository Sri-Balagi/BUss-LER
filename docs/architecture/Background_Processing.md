# Background Processing & Event Architecture

BizOS relies on an event-driven architecture to execute high-latency, AI-intensive tasks asynchronously. This ensures that the primary HTTP request lifecycle remains highly responsive.

## 1. Event Dispatching Abstraction

BizOS uses an internal Pub/Sub model via `AbstractEventDispatcher`. 

The current implementation uses `BackgroundTasksEventDispatcher`, which wraps FastAPI's native `BackgroundTasks`. This is deliberately designed as an abstraction so that in later phases, the exact same service code can trigger distributed jobs using external task queues like **Celery**, **RabbitMQ**, or **Kafka**.

### The Lifecycle Event Model
Instead of narrow event classes (e.g., `MemoryCreatedEvent`), BizOS uses a broader state-based event class: `MemoryLifecycleEvent`.
```python
class EventType(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```
This enables the event dispatcher to support `MemoryMerged`, `MemoryDeleted`, or `MemoryRestored` in the future without introducing new model paradigms.

## 2. Memory Processing Worker

The `MemoryProcessingWorker` is the first autonomous agent built into the platform.

### Responsibilities
1. Monitor `MemoryLifecycleEvent` (Specifically `CREATED`).
2. Coordinate with the `AIKernel` to summarize memory content.
3. Coordinate with the `AIKernel` to generate high-dimensional embeddings.
4. Orchestrate storage in PostgreSQL and Qdrant.
5. Provide strict idempotency and state guarantees.

### Idempotency & Concurrency Guarantees
Because events can theoretically be duplicated or re-delivered (especially if migrated to Celery/Kafka), the worker enforces strict idempotency:
- The worker immediately checks the `embedding_status` of the memory in PostgreSQL.
- If it is already `COMPLETED`, the worker silently exits.
- The worker transitions the memory from `PENDING` to `PROCESSING`, effectively placing a lock. If it succeeds, it sets it to `COMPLETED`.

### Error Handling and Retry Strategy
AI operations can fail due to network instability or provider rate limits.
- The worker wraps its execution block using the `tenacity` library.
- It applies **exponential backoff** with a maximum of 3 retries (configurable).
- If retries are completely exhausted, the memory's `embedding_status` is transitioned to `FAILED`, preventing silent zombie states.

## 3. Correlation Tracking

Every `DomainEvent` automatically generates a universally unique `correlation_id` at instantiation.

This `correlation_id` is propagated into the worker, which uses it to bind a structural logger context:
```python
log = logger.bind(
    correlation_id=event.correlation_id,
    memory_id=str(event.memory_id)
)
```
This ensures that all logs, from the initial API request across the background worker into AI responses, can be cleanly traced.
