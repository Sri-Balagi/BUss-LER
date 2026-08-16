# Qdrant Vector Infrastructure Layer

This document outlines the architecture, initialization flow, and extensibility strategy for the BizOS Vector Infrastructure Layer. This layer serves as the unified embedding backend for all BizOS components, including the Memory Engine, Goal Engine, Agent Contexts, and future simulation pipelines.

## Vector Infrastructure Overview
The Qdrant integration within BizOS adopts a strict **hybrid storage pattern**:
- **PostgreSQL**: The single source of truth for full record metadata and content.
- **Qdrant**: Acts strictly as the Semantic Index for vector representations and minimal filtering payloads.

The vectors strictly maintain a 1:1 UUID relationship with their PostgreSQL counterparts.

## Separation of Concerns
The Vector Repository explicitly adheres to the Single Responsibility Principle:
1. **Persistence Only**: It executes CRUD operations against Qdrant (`upsert`, `delete`, `query_points`).
2. **No Business Logic**: It does not interpret vectors or filter out results beneath arbitrary similarity thresholds.
3. **No AI Invocation**: It accepts pre-calculated floating-point arrays. The LLM or local embedding pipeline generates vectors earlier in the Service Layer.

## Initialization Flow
To guarantee idempotent and safe initialization across distributed deployments, Qdrant relies on the centralized `QdrantService` on startup:
```text
Application Start
      ↓
Initialize Qdrant (get_client)
      ↓
Check `collection_exists(memories)`
      ↓
[If Missing] Create collection (Cosine distance, configurable dimensions)
      ↓
[If Missing] Establish Payload indices (twin_id, memory_category, source)
      ↓
[If Missing] Store metadata (version: v1)
      ↓
Ready
```

## Abstract Repository Pattern
BizOS utilizes an `AbstractVectorRepository` interface to formalize interactions with vector databases. This ensures future portability across storage engines.

`MemoryVectorRepository` implements this interface exclusively for the `memories` context, ensuring that vectors inserted contain the exact expected schema.

## Schemas
### Configurable Dimensions
The vector dimension size (e.g., `768` for standard models, `1536` for OpenAI, `3072` for text-embedding-3-large) is fully dynamic. It is determined exclusively by the `qdrant_vector_size` environment configuration rather than hardcoded logic.

### Payload Schema
The vector payload includes only what is essential for query reduction (`must`/`should` queries) and recency weighting.
```json
{
  "memory_id": "UUID",
  "twin_id": "UUID",
  "memory_category": "observation",
  "source": "execution",
  "importance": 0.85,
  "created_at": "2026-06-25T14:00:00Z",
  "updated_at": "2026-06-25T14:00:00Z"
}
```

## Future Extensibility
While Phase 2 establishes `MemoryVectorRepository`, this generic infrastructure is designed to seamlessly support extending the ecosystem:
- **Goals**: `GoalVectorRepository` will utilize `goal_category` payloads for strategic planning indexing.
- **Agents**: `AgentContextRepository` will utilize `context_category` to represent short-term RAG loops during complex execution traces.
- **Simulation**: `SimulationVectorRepository` will embed simulation event histories to evaluate counterfactual scenarios using the identical underlying `AbstractVectorRepository` logic.
