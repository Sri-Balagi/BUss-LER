# Memory Experience API

## Overview
The Memory Experience API exposes the core capabilities of the BizOS Memory Engine. It provides a RESTful interface for external clients to create, query, list, retrieve, delete, and restore digital twin memories. 

This API is designed strictly as an experience layer and does not perform direct database or vector operations. Instead, it delegates all business logic and orchestrations to the internal `MemoryService`.

## Endpoints

### Health and Readiness
* `GET /api/v1/health/memory`: Returns the health status of the Memory Engine and its underlying subsystems (Metadata Repository, Vector Repository, AI Kernel).

### Memory Management
All operations are scoped to a specific Digital Twin.

* `POST /api/v1/twins/{twin_id}/memories`: Creates a new semantic memory for a twin. Triggers background summarization and embedding.
* `GET /api/v1/twins/{twin_id}/memories`: Lists memories for a twin with pagination and optional filtering by `category` and `include_deleted`.
* `POST /api/v1/twins/{twin_id}/memory/query`: Performs a semantic search against the twin's memories using natural language. Allows filtering by `category`, `min_importance`, and `threshold`.

### Single Memory Operations
* `GET /api/v1/memories/{memory_id}`: Retrieves a specific memory by ID.
* `DELETE /api/v1/memories/{memory_id}`: Soft deletes a memory from metadata and hard deletes it from the vector store.
* `POST /api/v1/memories/{memory_id}/restore`: Restores a previously deleted memory.
* `GET /api/v1/memories/{memory_id}/status`: Gets the background processing status (e.g. embedding status) of a memory.

## Key Architectural Principles

1. **Orchestration Only:** The API layer has no knowledge of Qdrant or Supabase. It only interacts with the `MemoryService`.
2. **Context Passing:** The `OperationContext` is built via dependency injection and propagated to the service layer for request tracing (generating an `X-Request-ID` header).
3. **Intent-Driven Design:** Endpoints use specific Commands and Queries (`MemorySearchQuery`, `CreateMemoryCommand`) instead of leaky DTOs.
4. **Rich Errors:** Standardized HTTP errors mapped from underlying `RepositoryError` and `ServiceError` exceptions.

## Next Steps
Future iterations will expose endpoints for the Goal Engine and the Simulation Engine, adhering to these same isolation patterns.
