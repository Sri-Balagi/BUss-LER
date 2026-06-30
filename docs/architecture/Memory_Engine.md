# Memory Service Architecture

BizOS employs a layered repository pattern, keeping business logic and service orchestration separate from data storage mechanics.

## 1. Overview & Responsibilities
The `MemoryService` acts as the **Memory Orchestrator**. It sits above the repository layer and acts as the singular entry point for memory management. 

**Responsibilities:**
- Coordinate between metadata repositories (`MemoryMetadataRepository`) and vector repositories (`MemoryVectorRepository`).
- Expose a clean, domain-centric API (e.g., `create_memory`, `search_memories`).
- Log execution latency, workflow orchestration, and domain failures.
- Bubble up cleanly mapped domain exceptions (`ServiceError`).

**What it explicitly avoids (Anti-Patterns):**
- It does **not** communicate directly with PostgreSQL or Qdrant.
- It does **not** generate vector embeddings.
- It does **not** generate AI summaries.
- It is **not** a "god class"; it is highly modular.

## 2. Separation of Operations
The `MemoryService` interface (`AbstractMemoryService`) enforces a strict boundary between mutating state and querying state.

### Write Operations
- `create_memory()`
- `delete_memory()`
- `restore_memory()`
- `update_summary()`
- `update_embedding_status()`

### Read Operations
- `get_memory()`
- `list_memories()`
- `search_memories()`

## 3. Dependency Injection
The Memory Engine relies exclusively on constructor-based dependency injection. Repositories are instantiated in `app/api/v1/dependencies.py` and passed into the `MemoryService`.

```text
MemoryService
 ├──> Metadata Repository (PostgreSQL)
 ├──> Vector Repository (Qdrant)
 ├──> (Phase 5) AI Kernel
 └──> (Phase 6) Background Event Publisher
```
This architecture guarantees that testing, mocking, and future evolution remain straight-forward.

## 4. Transaction Strategy & Orchestration Flows

### Creation Flow
Metadata insertion is synchronous, while vector embedding is delegated to asynchronous workers (Phase 6).

```text
Client -> create_memory()
            ↓
    MemoryMetadataRepository
            ↓
          Success
            ↓
    Return Memory object
```

### Search Flow (`search_memories`)
The service is repository-agnostic to the client. The client provides a raw query vector and expects unified `MemorySearchResult` objects.

```text
Query Vector
      ↓
Vector Repository (Qdrant search)
      ↓
Returns Memory IDs + Similarity Scores
      ↓
Metadata Repository (PostgreSQL get_by_id)
      ↓
Returns fully hydrated Memory Objects
      ↓
MemoryService unifies into `MemorySearchResults`
      ↓
Returns to Client
```

## 5. Security & Logging
The service strictly logs operational metadata (e.g. latency, object IDs, success/failure status) using structured logging. 

**Protected boundaries:**
- Raw embedding vectors are **never** logged.
- User-supplied memory text (`content`) is **never** logged.
- Large JSON payloads are **never** logged.
