# BizOS Memory Engine Testing Strategy

This document outlines the testing strategies and principles for the Memory Engine. It aligns with the AI Operating System vision of creating a resilient, scalable, and independent cognitive layer.

## 1. Testing Layers

The testing methodology is built on a layered approach:

### Unit Tests (`tests/api/`, `tests/services/`, `tests/workers/`)
* **Objective:** Validate isolated logic without side effects.
* **Scope:** Routers, Services, Repositories (mocks), Context parsing, Dependency injection.
* **Rules:**
  * Must be entirely asynchronous using `pytest-asyncio`.
  * External dependencies (PostgreSQL, Qdrant, AI Kernels) must be fully mocked.
  * Router tests must assert correct status codes and schema validation.

### Integration Tests (`tests/integration/`)
* **Objective:** Validate component boundaries and workflows.
* **Scope:** End-to-end memory pipeline (Router -> Event Bus -> Worker -> Service -> Repositories).
* **Rules:**
  * Use mocked Repositories to isolate logic flow.
  * Verify correct state transitions (`MemoryStateMachine`).

### End-to-End Tests (`tests/e2e/`)
* **Objective:** Verify user-facing behaviors.
* **Scope:** Simulated client flows (Create -> Retrieve -> Search -> Delete -> Status).
* **Rules:**
  * Test APIs using `FastAPI.TestClient`.
  * Can use in-memory databases (Sqlite, Qdrant `:memory:`) if configured, or mocks overriding the dependencies.

### Architecture Tests (`tests/architecture/`)
* **Objective:** Enforce dependency rules and domain isolation.
* **Scope:** Import statements and module boundaries.
* **Rules:**
  * Fail tests if Services import Routers.
  * Fail tests if Repositories import AI Kernel specific logic.
  * Enforce strict layer isolation.

### Chaos & Resilience Testing (`tests/chaos/`, `tests/resilience/`)
* **Objective:** Simulate outages and verify graceful degradation.
* **Scope:** Qdrant crashes, PostgreSQL timeouts, Duplicate event deliveries.
* **Rules:**
  * Ensure the Event Bus or Worker implements retry logic via `tenacity`.
  * Validate idempotency of background processes.

### Benchmark Testing (`tests/benchmarks/`)
* **Objective:** Measure latency under memory scaling.
* **Scope:** Vector Search performance with `10`, `100`, `1,000` memory points.
* **Rules:**
  * Ensure query execution remains under acceptable latency limits (`< 500ms`).

## 2. Infrastructure Considerations

* **AI Provider Mocking:** All automated tests must use a `MockAIKernel` to prevent real API costs and rate limiting during CI/CD.
* **Idempotency Check:** Background workers must gracefully handle re-delivered messages without double-processing data or corrupting the `EmbeddingStatus` state machine.
