# ADR-002: Introduce Kernel Abstractions

## Status
Accepted

## Context
BizOS is maturing from a pipeline of cognitive engines into a true Universal AI Operating System. For Wave-2 and beyond, we must decouple the core OS logic from application-level agents, workflows, and infrastructure. We need robust abstractions to isolate failures and manage multi-agent environments securely.

## Decision
We will introduce a dedicated Kernel package at `app/runtime/kernel/` containing foundational abstractions inspired by traditional operating systems.

Key additions:
1. **Process Management:** `ProcessControlBlock` (PCB), `ProcessTable`, and `ProcessState` to formalize how active tasks, workflows, and agents are tracked in memory.
2. **System Calls:** `ISyscallInterface` defining the exact boundaries where untrusted code (agents/plugins) requests privileges from the OS.
3. **Kernel Rings:** Formal isolation levels (Ring 0 to Ring 3) mapping to core OS, system services, and untrusted execution contexts.
4. **Virtual Filesystem (VFS):** An abstraction layer preventing agents from knowing whether they are writing to PostgreSQL, Qdrant, or local disk.

## Consequences
**Positive:**
- Lays the bedrock for distributed execution (Swarms) and secure sandboxing.
- Agents will no longer interact directly with the DB; they will trap into the Kernel via Syscalls or VFS paths.
- Clean Architecture is strictly enforced.

**Negative:**
- Short-term architectural overhead.
- Existing Wave-1 pipeline components will need to be eventually wrapped in `ProcessControlBlocks` to be tracked by the new `RuntimeManager`.
