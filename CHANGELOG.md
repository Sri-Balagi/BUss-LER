# BizOS Changelog

All notable changes to the BizOS API Operating System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-26

### Added
- **Memory Engine**: Introduced semantic memory capabilities for Digital Twins.
- **AI Kernel Abstraction**: Replaced direct API bindings with `AbstractAIKernel` supporting multiple providers (Gemini primary).
- **Event-Driven Processing**: Implemented asynchronous memory processing via `EventBus` and `BackgroundTasksDispatcher`.
- **Vector Storage**: Integrated Qdrant for semantic similarity search.
- **Memory Experience API**: Published `/api/v1/twins/{twin_id}/memory` endpoint for memory ingestion, querying, and management.
- **State Machine**: Introduced `MemoryStateMachine` for reliable memory lifecycle tracking (PENDING, PROCESSING, COMPLETED, FAILED).
- **Operation Context**: Introduced thread-safe request correlation.

### Changed
- Layered Architecture strictly enforced across API, Services, Repositories, and Providers.
- Transitioned background tasks to `tenacity`-backed resilience loops.

## [1.0.0] - Foundation

### Added
- **Digital Twin Foundation**: Core `Twin` entity and CRUD capabilities.
- Supabase PostgreSQL integration via `supabase-py`.
- FastAPI foundational layer.
