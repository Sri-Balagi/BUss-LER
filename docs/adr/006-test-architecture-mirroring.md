# ADR-006: Test Architecture Mirroring

**Status:** Accepted | **Date:** 2026-06-29

## Context
Tests organized by type (unit/integration/e2e) made it hard to locate tests for a specific component and did not enforce co-location of tests with production code.

## Decision
Mirror production package structure exactly in tests/: tests/runtime/ mirrors app/runtime/, tests/intelligence/ mirrors app/intelligence/, etc. Cross-layer tests live in tests/certification/.

## Consequences
- Tests always co-located with components they test
- CI can run layer-specific subsets (pytest tests/runtime/)
- Certification tests explicitly separated from unit tests
