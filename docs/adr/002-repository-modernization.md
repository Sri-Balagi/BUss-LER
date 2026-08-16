# ADR-002: Repository Modernization from FastAPI to AI OS Layout

**Status:** Accepted | **Date:** 2026-06-29

## Context
The original repository used the standard FastAPI layout (app/api/, app/services/, app/repositories/, app/models/). As BizOS became a full AI OS, this structure obscured architecture and confused contributors.

## Decision
Refactor to kernel-based layout: app/api/ -> app/interfaces/http/, app/services/ -> app/intelligence/ + app/runtime/, app/repositories/ -> app/infrastructure/persistence/, app/models/ distributed to bounded contexts.

## Consequences
- Repository structure communicates the architecture
- 367 tests validated with zero regressions post-migration
- Legacy technical debt eliminated
