# BizOS v6.0.0 — Architecture Reference

**Version:** 6.0.0
**Status:** FROZEN
**Date:** 2026-06-29

---

## 1. Introduction

BizOS is an AI Operating System designed to model, understand, and autonomously serve entities (businesses, individuals, organizations). It provides the architectural foundation for AI agents to operate with persistent memory, stateful execution, strategic reasoning, and provider-agnostic cognitive capabilities.

This document is the canonical architecture reference for BizOS v6.0.0. It describes every architectural layer, the design rationale behind key decisions, approved communication patterns, and extension points for future development.

---

## 2. Architectural Philosophy

BizOS is designed around three core principles:

**1. Kernel Isolation**
The system separates *runtime execution* (how agents do things) from *executive intelligence* (what agents should do and why). These two concerns are implemented in separate, independently deployable kernels that cannot import from each other except through a single approved bridge interface.

**2. Domain-Driven Boundaries**
Each kernel is partitioned into bounded contexts (intake, strategy, decision, learning, etc.). These contexts own their data models, business logic, and interfaces. They do not share internal state or implementation.

**3. Infrastructure Independence**
All persistence, AI provider calls, caching, and messaging concerns are isolated in the infrastructure layer. Neither kernel imports directly from providers — they depend only on abstractions defined within their own boundaries.

---

## 3. System Layers

`
┌────────────────────────────────────────────────────────────────────┐
│                     Interfaces Layer                               │
│              (HTTP API, future CLI, future SDK)                    │
└───────────────────────────────┬────────────────────────────────────┘
                                │ inward only
        ┌───────────────────────┼──────────────────────────┐
        │                       │                          │
┌───────▼──────────┐    ┌───────▼──────────┐    ┌─────────▼────────┐
│   Intelligence   │    │    Runtime OS    │    │    Platform      │
│   Kernel (M6)    │◄──►│    Kernel (M5)   │    │  Config, DI,     │
│                  │    │                  │    │  Telemetry       │
└───────┬──────────┘    └────────┬─────────┘    └──────────────────┘
        │ via bridge only        │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────┐
        │   Infrastructure       │
        │  AI · DB · Vector      │
        └────────────────────────┘
                    │
        ┌───────────▼────────────┐
        │   Shared Primitives    │
        │  Enums, Events, Errors │
        └────────────────────────┘
`

---

## 4. Runtime OS Kernel (M5)

### Purpose
The Runtime Kernel is the execution substrate of BizOS. It manages how AI agents consume capabilities, execute tasks, track budgets, manage sessions, and respect policies.

### Bounded Contexts

| Context | Responsibility |
|---------|---------------|
| gents/ | Agent identity, registration, lifecycle |
| capabilities/ | Capability registry, resolution, version management |
| 	asks/ | DAG-based task definition and execution |
| scheduler/ | Priority-based async task scheduling |
| udget/ | Token, time, and resource budget enforcement |
| session/ | Execution session isolation and lifecycle |
| queues/ | Task queuing with priority lanes |
| etry/ | Exponential backoff, circuit breaker, jitter |
| policies/ | Configurable runtime policy enforcement |

### Key Contracts
- The Runtime Kernel **never imports from Intelligence**. It defines execution contracts that Intelligence fulfills through the bridge.
- All task execution flows through the DAG engine — no imperative sequencing.
- Capabilities are registered, not hardcoded. Extensions add new capabilities without modifying the kernel.

---

## 5. Executive Intelligence Kernel (M6)

### Purpose
The Intelligence Kernel is the cognitive substrate of BizOS. It classifies intent, builds context, forms strategy, generates plans, produces recommendations, learns from outcomes, and governs compliance.

### Bounded Contexts

| Context | Responsibility |
|---------|---------------|
| intake/ | Intent classification, context assembly, situation awareness |
| strategy/ | Goal management, strategic planning, priority reasoning |
| decision/ | Plan generation, recommendation engine |
| learning/ | Memory management, cognitive trace, outcome tracking |
| oversight/ | Governance, compliance, audit |
| workspaces/ | Multi-entity workspace isolation |
| untime_bridge/ | **Only approved integration point with Runtime** |

### Runtime Bridge Contract
Intelligence communicates with Runtime exclusively through pp/intelligence/runtime_bridge/.
This bridge exposes a typed interface that Runtime publishes and Intelligence consumes.
No other cross-kernel imports are permitted.

---

## 6. Infrastructure Layer

### Purpose
The Infrastructure Layer provides concrete implementations of all I/O concerns: AI provider calls, database persistence, vector search, and caching.

### Subsystems

| Subsystem | Implementation |
|-----------|---------------|
| i/ | AI Kernel abstraction + Gemini provider |
| persistence/postgres/ | Supabase-backed PostgreSQL repositories |
| ectorstore/ | Qdrant vector search integration |
| cache/ | In-memory context caching with TTL |

### AI Kernel Design
The AI Kernel (AbstractAIKernel) exposes three capabilities:
- generate(AIRequest) — text generation
- embed(EmbeddingRequest) — vector embedding
- classify(ClassifyRequest) — structured JSON classification

All capabilities are provider-agnostic. Adding a new LLM provider requires only implementing the AbstractAIProvider interface.

---

## 7. Shared Layer

The shared layer contains primitives that are genuinely universal: domain enumerations, domain events, and domain exceptions.

**Rules:**
- Any module may import from shared/.
- shared/ may never import from any other layer.
- If a primitive is specific to one kernel, it belongs in that kernel, not shared.

---

## 8. Dependency Rules (Enforced)

`
shared      → (nothing)
infrastructure → shared
runtime     → shared, infrastructure
intelligence → shared, infrastructure, runtime (via bridge only)
interfaces  → shared, intelligence, runtime
platform    → shared
bootstrap   → everything (composition only)
`

Violations of these rules constitute architecture boundary violations and must be corrected before any release.

---

## 9. Extension Points

| Extension Type | Mechanism |
|---------------|-----------|
| New AI provider | Implement AbstractAIProvider, register in DI |
| New capability | Implement AbstractCapability, register in CapabilityRegistry |
| New agent type | Implement AbstractAgent, register in AgentRegistry |
| New context provider | Implement AbstractContextProvider, register in ContextProviderRegistry |
| New HTTP endpoint | Add router to interfaces/http/v1/routers/ |

---

## 10. Future Roadmap

| Area | Description |
|------|-------------|
| CLI Interface | Implement pp/interfaces/cli/ (namespace reserved) |
| SDK | Implement pp/interfaces/sdk/ (namespace reserved) |
| File Storage | Implement pp/infrastructure/storage/ (namespace reserved) |
| Messaging Bus | Implement pp/infrastructure/messaging/ (namespace reserved) |
| Multi-Provider Routing | Add provider selection logic to i/router.py |
| Real-time Streaming | Add SSE/WebSocket support to interfaces layer |
