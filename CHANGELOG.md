# Changelog

All notable changes to BizOS are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.0.0] — 2026-06-29

### Summary
BizOS v6.0.0 is the production freeze of the dual-kernel AI Operating System architecture.
Both the Runtime OS Kernel (M5) and Executive Intelligence Kernel (M6) are complete and frozen.

### Added — M6 Executive Intelligence Kernel
- **Intent Classifier**: AI-powered business intent classification engine
- **Context Assembler**: EnterpriseContext assembly from cognitive subsystems
- **Planning Engine**: Goal-to-plan decomposition with AI reasoning
- **Recommendation Engine**: Proactive opportunity and risk recommendation
- **Cognitive Trace**: Full audit trail of AI reasoning and decisions
- **Goal Management**: Strategic, tactical, and operational goal lifecycle
- **Learning Repository**: Outcome tracking and model improvement hooks
- **Workspace Management**: Multi-entity workspace isolation
- **Oversight Layer**: Governance, compliance, and policy enforcement
- **Runtime Bridge**: Strictly-typed integration channel to M5

### Added — M5 Runtime OS Kernel
- **Agent Registry**: Dynamic agent identity and lifecycle management
- **Capability Manager**: Plugin-style capability registration and resolution
- **Task DAG Engine**: Directed acyclic graph task execution
- **Scheduler**: Priority-based asynchronous task scheduling
- **Budget Manager**: Token and resource budget enforcement
- **Session Manager**: Execution session isolation and lifecycle
- **Policy Engine**: Configurable execution policy enforcement
- **Queue Manager**: Task queuing with priority lanes
- **Retry Engine**: Exponential backoff with circuit breaker

### Changed — Repository Modernization (Phases 1–12)
- Complete repository restructure from legacy FastAPI layout to AI OS architecture
- Eliminated 30+ modernization scripts from repository root
- Reorganized test hierarchy to exactly mirror production packages
- Consolidated duplicate enums, error handlers, and model classes
- Updated pyproject.toml version from 4.0.0 to 6.0.0

### Removed
- Legacy pp/services/ package (replaced by kernel-based architecture)
- Legacy pp/repositories/ package (moved to pp/infrastructure/persistence/)
- Legacy pp/api/ package (moved to pp/interfaces/http/)
- Legacy pp/models/ package (distributed to bounded contexts)
- All modernization scripts (un_phase*.py, ix_*.py, udit_*.py, etc.)

---

## [5.0.0] — 2026-06-28

### Summary
M5 Runtime OS Kernel — production-complete runtime execution platform.

---

## [4.0.0] — 2026-06-26

### Summary
M4 Context Engine — intelligent context assembly for AI decision-making.
EnterpriseContext: intent, goals, plans, recommendations, memory, conversation, and trace integration.

---

## [3.0.0] — 2026-06-26

### Summary
M3 AI Kernel — provider-agnostic AI capability abstraction.
Gemini integration. Structured classification. Prompt management system.

---

## [2.0.0] — 2026-06-25

### Summary
M2 Memory Engine — semantic memory with vector embeddings.
Qdrant integration. Memory summarization. Cognitive trace foundation.

---

## [1.0.0] — 2026-06-24

### Summary
M1 Digital Twin Foundation.
Entity modeling. Goal tracking. Supabase persistence layer.

---

## [0.1.0] — 2026-06-24

### Summary
M0 Project foundation. FastAPI scaffold. Environment configuration.
