# BizOS Operational Runbook

## 1. Routine Operations
### 1.1 Application Startup
```bash
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000
```
### 1.2 Graceful Shutdown
Send `SIGTERM` to the FastAPI process. The Event Bus will drain, and database connections will close safely.

## 2. Monitoring
BizOS exposes operational metrics through its architecture:
- **Health Check**: `GET /health` (Returns version and subsystem status).
- **Context Graph Latency**: Graph traversal times are logged at `INFO` level. Look for `[ContextEngine] Graph built in ...ms`.
- **Cache Hit Rates**: Logged via `ContextCache`. Monitoring `redis` or `pgvector` query frequency will indicate cache eviction issues.

## 3. Recovery & Troubleshooting
### 3.1 Provider Failures
If an external `ContextProvider` fails (e.g., Third-party API is down):
- If the provider is marked `required=True`, the entire Context Graph will abort and throw a `ContextGenerationError`.
- If the provider is marked `required=False`, the graph logs a warning, skips the provider, and continues assembling the partial `EnterpriseContext`.

### 3.2 Cache Eviction / Stale Context
If the LLM is acting on stale memory:
1. Verify the Event Bus is actively receiving invalidation events.
2. Manually invalidate a specific entity's cache via the internal API or DB wipe.
3. Re-trigger the graph to rebuild the `EnterpriseContext` from source.

## 4. Context Rebuilding (Maintenance)
If the schema of `EnterpriseContext` changes in future versions, you must wipe the intermediate cache stores (Redis/Postgres JSONB context cache) to force all entities to rebuild through the new Context Dependency Graph on their next request.
