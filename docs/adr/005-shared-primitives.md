# ADR-005: Shared Primitives vs Bounded Context Models

**Status:** Accepted | **Date:** 2026-06-29

## Context
Central app/models/ created hidden coupling between domains.

## Decision
Distribute all domain models to their owning bounded contexts. Only genuinely universal primitives belong in app/shared/: cross-domain enumerations, domain event bus, and error hierarchy.

## Consequences
- Models live beside the code that owns them
- Shared layer stays minimal and stable
- Import analysis detects boundary violations automatically
