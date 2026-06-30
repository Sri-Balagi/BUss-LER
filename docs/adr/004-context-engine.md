# ADR-004: EnterpriseContext Assembly Pattern

**Status:** Accepted | **Date:** 2026-06-26

## Context
AI models make poor decisions without sufficient grounded context. BizOS needed a mechanism to assemble all relevant entity state into a coherent context package.

## Decision
Implement EnterpriseContext composed of ContextSection objects contributed by registered AbstractContextProviders. A ContextAssembler orchestrates provider execution, caches results, and passes assembled context to the AI Kernel.

## Consequences
- AI prompts always grounded in real entity state
- New context sources register without modifying the assembler
- Context caching is critical — assembly is the most expensive operation
