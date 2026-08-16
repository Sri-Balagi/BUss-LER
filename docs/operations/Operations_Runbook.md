# BizOS Memory Engine Operations Runbook

This runbook outlines standard operating procedures for the BizOS Memory Engine.

## 1. Health Monitoring

### Endpoint Verification
The primary health endpoint is `GET /api/v1/health/memory`.

**Expected Output (Healthy):**
```json
{
  "status": "healthy",
  "subsystems": {
    "metadata_repository": "healthy (45.2ms)",
    "vector_repository": "healthy (12.1ms)",
    "ai_kernel": "healthy"
  }
}
```

**Degraded Output:**
If one subsystem is offline, the status shifts to `degraded`. The API will continue serving what it can (e.g., accepting creation requests without vector searching).

## 2. Common Operational Issues

### 2.1 Missing Migrations (PGRST205)
**Symptom:** `/health/memory` shows `metadata_repository` is `unhealthy` with message: `Could not find the table 'public.memories' in the schema cache`.
**Action:** Apply `migrations/002_memory_engine_schema.sql` via Supabase Dashboard SQL Editor, and reload the Supabase schema cache.

### 2.2 Vector Database Unreachable
**Symptom:** Qdrant logs connection timeouts or `vector_repository` shows `unhealthy`.
**Action:** Restart the Qdrant container (`docker restart bizos-qdrant`). Wait 10 seconds for initialization. 

### 2.3 AI Provider Rate Limiting (503 / 429)
**Symptom:** AI Kernel reports `503 Unavailable` or `429 Too Many Requests`.
**Action:** This is an upstream Gemini/OpenAI issue. The `MemoryProcessingWorker` implements `tenacity` retries and will attempt exponential backoff. No direct manual action needed unless the outage exceeds the retry limit (defaults to ~3 retries), at which point state becomes `FAILED`.

## 3. Incident Response & Recovery Workflows

### Worker Queue Stalled
If memories are staying in `PENDING` indefinitely:
1. Check the logs for the Worker container. 
2. Ensure the Event Bus is actively delivering messages.
3. Restart the Worker container. The `MemoryStateMachine` idempotency checks guarantee no data will be corrupted upon restart.

### FAILED Memory Processing
If memories reach `FAILED` status due to persistent upstream outages:
1. Connect to the metadata database.
2. Run: `UPDATE memories SET embedding_status = 'PENDING' WHERE embedding_status = 'FAILED';`
3. The background worker or nightly sweep will automatically re-process these events cleanly.

## 4. Maintenance Procedures

* **Vector Reindexing:** Qdrant collections handle continuous writes effectively. Full reindexing is only required if the underlying embedding model (`gemini-embedding-001`) changes.
* **Environment Variable Rotation:** Updating `GEMINI_API_KEY` requires restarting both the API and Worker containers.
