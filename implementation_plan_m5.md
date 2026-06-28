# BizOS M5: Stage 1 (Foundation) Implementation Plan

As per the hybrid implementation strategy, this plan covers **Stage 1 (Foundation)** of the M5 Agent Runtime framework. The objective is to define the core structural interfaces of the Execution Kernel before any specific execution tracks (Schedulers, Agents, Tools) are built. 

These interfaces will become frozen and immutable for the remainder of M5.

## 1. Summary of Implementation
We will implement the pure abstractions and core models that define the execution runtime boundary. No logic or infrastructural dependencies (e.g., actual Agent orchestration) will be introduced in this stage. 

The deliverables are:
- `ExecutionSession`: The root container that scopes an execution.
- `WorkingMemory`: The ephemeral memory sandbox.
- `ExecutionBudget`: Resource bounding limits (tokens, time, steps).
- `CancellationToken`: Standardized abort signaling.
- Base Exceptions, runtime state enums, and DI interfaces.

## 2. Affected Packages
All code for the execution kernel will live under a new namespace: `app/runtime`.

### [NEW] `app/runtime/models/exceptions.py`
- Core base exceptions: `ExecutionError`, `BudgetExceededError`, `AgentSuspendedError`.

### [NEW] `app/runtime/models/enums.py`
- Execution states: `TaskState` (PENDING, RUNNING, SUSPENDED_FOR_APPROVAL, COMPLETED, FAILED), `AgentState`.

### [NEW] `app/runtime/models/budget.py`
- `ExecutionBudget` pydantic model (max_tokens, max_time_ms, max_recursion).

### [NEW] `app/runtime/session/cancellation.py`
- `CancellationToken` abstraction for signaling abort down the DAG.

### [NEW] `app/runtime/session/working_memory.py`
- `WorkingMemory` abstraction (get, set, list, clear).

### [NEW] `app/runtime/session/execution_session.py`
- `ExecutionSession` containing the budget, token, working memory, and session metadata.

### [NEW] `app/runtime/core/di.py`
- Base registration routines for injecting the Session into the broader `app.core.dependencies` lifecycle.

## 3. Dependencies
- **Pydantic**: For strict validation of models (`ExecutionBudget`, `ExecutionSession`).
- **Core Exceptions / Logging**: Extending from existing `bizos.models.exceptions.BaseBizOSError` to maintain architectural consistency.
- No direct dependencies on the M4 Context Engine are instantiated here; these are pure execution primitives that M4 and M3 components will eventually be wrapped in.

## 4. Architectural Reasoning
By starting strictly with the `ExecutionSession` and `WorkingMemory` interfaces, we force the subsequent development tracks (Tasks, Tools, Agents) to program against these locked contracts. 
- A tool cannot run without an `ExecutionSession` (giving it access to cancellation tokens).
- A task cannot run without an `ExecutionBudget`.
This prevents "architectural drift" during parallel subsystem implementation.

## Verification Plan
1. Ensure `ruff check` and `ruff format` are clean.
2. Verify dependency graph rules (e.g. `app.runtime` does not incorrectly depend on `app.api`).
3. Complete unit tests for basic budget arithmetic and cancellation token states.

---
## User Review Required
Please review the Stage 1 implementation boundaries. Click **Proceed** to authorize the implementation of the core foundation interfaces!
