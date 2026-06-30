# Architecture Freeze (v4.0.0)

With the release of BizOS v4.0.0, the Enterprise Context Engine architecture is formally frozen. This document outlines the invariants that must not be violated by future milestones or PRs.

## Frozen Interfaces
- `app.services.providers.base.ContextProvider`: The abstract base class is locked. Any new provider MUST inherit from this and implement `async def build_context(...)`.
- `app.models.enterprise_context.EnterpriseContext`: The pydantic envelope is strictly immutable (`frozen=True`). No logic should attempt to mutate properties on this object after it is instantiated.
- `app.services.context_engine.ContextEngine`: The primary orchestrator API is frozen.

## Architectural Invariants
1. **No Circular Dependencies**: Context Providers must not depend on each other cyclically. The dependency graph must remain a DAG.
2. **LLM Isolation**: Context Providers and the Context Engine MUST NOT import or directly invoke the LLM integration layer (`PromptManager`, `AIKernel`). They only prepare the data envelope.
3. **Fail-Fast vs Soft-Fail**: Providers must correctly configure `required=True/False` so the graph knows whether to abort context generation if a third-party API goes down.

## Extension Points
Future features (Milestone 5) must extend through these designated points:
- Registering a new `ContextProvider` in the `ProviderRegistry`.
- Registering a new `ContextStrategy` in the `StrategyRegistry`.
- Subscribing to the Event Bus for context invalidation events.

## Prohibited Dependency Directions
- ❌ **Downstream to Upstream**: The Prompt Generation layer cannot reach back into the Context Providers to fetch more data. All required data must be packaged inside the `EnterpriseContext`.
- ❌ **Sibling Coupling**: `MemoryProvider` cannot directly import `ActivityProvider`. They must pass data strictly through the Dependency Graph metadata.
