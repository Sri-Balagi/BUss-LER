# BizOS Architecture Index

This is the primary navigation hub for all technical documentation related to the BizOS AI Operating System. 

## Core Subsystems

* **[AI Kernel](AI_Kernel.md)** - The provider-agnostic abstraction layer for foundation models (LLMs, Embeddings).
* **[Memory Engine](Memory_Engine.md)** - The central orchestration service for digital twin experiences, taxonomy, and lifecycle management.
* **[Background Processing](Background_Processing.md)** - The event-driven architecture, resilient worker pools, and task dispatching logic.
* **[Repository Architecture](Repository_Architecture.md)** - Abstractions for metadata persistence (Supabase/PostgreSQL).
* **[Qdrant Architecture](Qdrant_Architecture.md)** - Vector database integration and semantic indexing strategy.

## API & Testing

* **[API Reference](API_Reference.md)** - Contracts, routing, and DTOs for the public Memory Experience REST API.
* **[Testing Strategy](Testing_Strategy.md)** - The testing matrix (Unit, Integration, E2E, Resilience, Chaos, Architecture) and methodology.
* **[Architecture Audit Report](Architecture_Audit_Report.md)** - Comprehensive, unbiased evaluation of the BizOS codebase and readiness for future milestones.

## Operations & Deployment

* **[Production Deployment Guide](Production_Deployment_Guide.md)** - Strategies for containerized and PaaS deployments.
* **[Operations Runbook](Operations_Runbook.md)** - Health monitoring, recovery workflows, and troubleshooting.
* **[Configuration Reference](Configuration_Reference.md)** - The environment variable matrix.
* **[Deployment Checklist](Deployment_Checklist.md)** - Step-by-step rollout procedures for releases.

## Architecture Decision Records (ADRs)

Located in `docs/architecture/decision-records/`:
* `ADR-001_Why_Digital_Twins.md`
* `ADR-002_Why_Supabase_PostgreSQL.md`
* `ADR-003_Why_Repository_Pattern.md`
* `ADR-004_Why_Optimistic_Concurrency.md`
* `ADR-005_Why_Qdrant.md`
* `ADR-006_Why_Strict_Layered_Architecture.md`
* `ADR-007_Why_AI_Kernel.md`
* `ADR-008_Why_Event_Driven_Architecture.md`
* `ADR-009_Why_Local_AI_Support.md`
* `ADR-010_Why_Domain_Agnostic_Design.md`

## Stable Interfaces (v2.0.0)

The following core interfaces are frozen and certified stable as of v2.0.0:
* `AbstractMemoryRepository`
* `AbstractVectorRepository`
* `AbstractAIKernel`
* `EventBus`
* `MemoryService`
* `OperationContext`
* Public REST API contracts under `/api/v1`

These interfaces should only be extended—not broken—in future milestones.
