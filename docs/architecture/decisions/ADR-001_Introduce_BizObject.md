# ADR-001: Introduce BizObject

## Status
Accepted

## Context
As BizOS evolves into a Universal AI Operating System, the number of distinct entities (Digital Twin, Cognitive Session, Workflow, Capability, Task, Agent) has grown. To ensure strict consistency, deterministic serialization, and universal ownership tracking over the next 10+ years, we need a root base class that all core OS domain models inherit from. 

Without a universal base object, components across distributed K8s K8s environments cannot guarantee how identities, timestamps, and metadata are represented on the System Bus.

## Decision
We will introduce `BizObject` as the root domain entity in `app/domain/common/biz_object.py`.

Every domain entity MUST inherit from `BizObject` or a subclass of it.

`BizObject` will enforce the following immutable properties:
- `id`: Unique `uuid.uuid4()`.
- `tenant_id`: Identifier for the overarching tenant organization.
- `owner_id`: Specific UUID of the user/entity that owns this object.
- `correlation_id`: Used for distributed tracing across workflows.
- `version`: Integer for optimistic concurrency control.
- `metadata`: Arbitrary key-value dictionary for extensibility.
- `tags`: List of string labels.
- `created_at`: UTC timestamp of creation.
- `updated_at`: UTC timestamp of the last modification.

## Consequences
**Positive:**
- Guaranteed consistency across the entire OS.
- Simplifies the API Gateway and Virtual Filesystem (VFS) which can now assume all payloads have an `id` and `tenant_id`.
- Distributed tracing is natively supported via `correlation_id`.

**Negative:**
- All existing Wave-1 entities will eventually need to be refactored to inherit from `BizObject`. (We will do this iteratively).
