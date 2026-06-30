# ADR-003: Provider-Agnostic AI Kernel

**Status:** Accepted | **Date:** 2026-06-26

## Context
Vendor lock-in to Google Gemini would make BizOS fragile to pricing changes, API deprecations, and capability gaps.

## Decision
Implement AbstractAIKernel with generate(), embed(), and classify() methods. All providers implement AbstractAIProvider. Business logic never imports a provider directly.

## Consequences
- Any LLM can be added without modifying business logic
- Classification responses always validated as structured JSON
- Provider selection configurable at runtime
