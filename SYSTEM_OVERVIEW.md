# BizOS — System Architecture Overview

BizOS is an AI Operating System for Entities. This document describes the complete
architecture from HTTP interface to infrastructure, without implementation details.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  INTERFACES                                                  │
│  REST API · CLI · SDK                                        │
│  (FastAPI routes, request validation, response serialization)│
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP / internal calls
┌─────────────────────▼───────────────────────────────────────┐
│  EXECUTIVE INTELLIGENCE KERNEL  [M6 — FROZEN]               │
│  Strategy · Decision · Learning · Context · Planning         │
│  (What should the entity do?)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ Runtime Bridge (typed interface only)
┌─────────────────────▼───────────────────────────────────────┐
│  RUNTIME KERNEL  [M5 — FROZEN]                              │
│  Agents · Tasks · Scheduler · Events · Sessions · Queues    │
│  (How does the entity do it?)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ Repository/Provider abstractions
┌─────────────────────▼───────────────────────────────────────┐
│  INFRASTRUCTURE                                              │
│  Supabase · Qdrant · Gemini · Cache · Migration             │
│  (External system adapters)                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ shared primitives
┌─────────────────────▼───────────────────────────────────────┐
│  SHARED                                                      │
│  Enumerations · Events · Exceptions · IDs                   │
│  (Cross-cutting primitives with no business logic)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### Interfaces
Entry points for all external consumers. Responsible for:
- HTTP request validation and response serialization
- Dependency injection (resolving kernel/service instances)
- API versioning (`/api/v1/`)
- Authentication and authorization enforcement
- Observability middleware (request IDs, metrics, logging)

### Executive Intelligence Kernel (M6)
The cognitive substrate. Responsible for:
- **Strategy**: Goal-setting, priority management, strategic direction
- **Decision**: Action selection, decision rationale, confidence scoring
- **Learning**: Experience capture, performance improvement, model tuning
- **Context**: Enterprise context assembly (EnterpriseContext)
- **Planning**: Task decomposition, roadmap generation

The intelligence kernel **never communicates with infrastructure directly**.
All execution is delegated to the Runtime Kernel via the **Runtime Bridge**.

### Runtime Kernel (M5)
The execution substrate. Responsible for:
- **Agents**: Agent lifecycle, capability registration, execution dispatch
- **Tasks**: DAG-based task execution, dependency resolution
- **Scheduler**: Async job scheduling, cron-like execution
- **Events**: Typed event bus, publish/subscribe
- **Sessions**: Execution sessions, working memory, cancellation
- **Queues**: Message queuing, priority handling
- **Retry**: Configurable retry policies with exponential backoff

The runtime kernel does **not import from the Intelligence kernel**.

### Runtime Bridge
The only authorized communication channel between Intelligence and Runtime.
- Typed interface only (no concrete kernel types cross the boundary)
- One-way: Intelligence → Runtime
- All cross-kernel calls pass through `app/runtime/bridge/`

### Infrastructure
External system adapters. Responsible for:
- Supabase PostgreSQL persistence (entities, goals, memory, conversations)
- Qdrant vector store (embeddings, semantic search)
- Gemini AI provider (generation, embedding, classification)
- Cache layer (in-memory and distributed caching)

Infrastructure depends only on domain interfaces — it is never imported by kernels directly.

### Shared
Cross-cutting primitives shared across all layers:
- `enums.py` — system-wide enumerations
- `events/bus.py` — typed event bus
- `exceptions/errors.py` — error hierarchy
- `ids/` — ID generation utilities

Shared contains **zero business logic**.

---

## Dependency Rules

| Layer | May Import From |
|-------|----------------|
| Interfaces | Intelligence (via DI), Runtime Bridge, Shared, Platform |
| Intelligence | Runtime Bridge, Shared |
| Runtime | Shared |
| Infrastructure | Shared |
| Shared | Nothing (stdlib only) |
| Platform | Shared |

**Violations of these rules are architectural regressions.**

---

## Observability Stack

| Concern | Implementation |
|---------|---------------|
| Structured logging | structlog (JSON in production) |
| Request tracing | X-Request-ID + X-Correlation-ID headers |
| Metrics | Prometheus (`/metrics`) |
| Distributed tracing | OpenTelemetry (optional, OTEL_ENABLED=false default) |
| Health probes | `/api/v1/health`, `/api/v1/live`, `/api/v1/ready` |

---

## Deployment Topology

```
[Internet]
    │
    ▼
[Load Balancer / Nginx]
    │
    ▼
[BizOS API Container(s)]  ─── [Qdrant Vector Store]
    │
    ├── [Supabase Cloud (PostgreSQL)]
    └── [Gemini API (Google AI)]
```

For full deployment details, see `docs/operations/deployment.md`.