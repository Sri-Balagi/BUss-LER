# BizOS Memory Engine Production Deployment Guide

BizOS follows an event-driven service architecture, consisting of a FastAPI web layer, background worker processes, and managed persistence layers.

## 1. Supported Deployment Strategies

### Containerized Deployment (Recommended)
You can deploy BizOS entirely within Docker, bridging application containers with your managed data stores.

* **API Container:** Runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`
* **Worker Container:** Runs the same image but with a worker entrypoint (e.g., `python -m app.workers.memory_worker`)
* **Qdrant:** Deployed alongside containers via standard Docker network (or managed via Qdrant Cloud).
* **Supabase:** Managed cloud instance.

### PaaS Deployment
Platforms like Render, Heroku, or AWS App Runner can naturally host BizOS:
* Define your web service start command (`uvicorn`).
* Define a background service pointing to the worker script.
* Supply environment variables (see `Configuration_Reference.md`) securely via platform secrets.

## 2. Environment Setup

Copy the example configuration to your secure secret manager or `.env` file (if using Docker Compose).

```bash
cp .env.example .env
```

Ensure `SUPABASE_URL`, `SUPABASE_KEY`, and `GEMINI_API_KEY` are populated.

## 3. Database Initialization

Because BizOS utilizes Supabase, database migrations are applied via the Supabase CLI or SQL Editor:

1. Locate the SQL scripts in the `migrations/` directory.
2. Execute `001_digital_twin_schema.sql` and `002_memory_engine_schema.sql` against your remote Postgres instance.
3. Verify that the `entities`, `twins`, and `memories` tables exist.

## 4. Startup Sequence

1. **Start Qdrant:** Ensure the vector database is accepting requests on port `6333`.
2. **Start Background Worker:** Initialize the worker process. It will gracefully idle if the Event Bus is empty.
3. **Start FastAPI:** Boot the web API. It will synchronously validate the environment variables before binding to the port.

## 5. Shutdown Sequence & Cleanup

1. Send `SIGTERM` to the FastAPI process. The router gracefully drains active requests.
2. Send `SIGTERM` to the Background Worker. Running processing jobs finish the current transaction; pending events remain in the queue or fall back to DB.
3. Do not forcefully kill containers without a graceful timeout (~15s) to avoid orphan state.

## 6. Recovery Procedures

* **PostgreSQL Loss:** API will reject writes with `503 Service Unavailable`. Recovery is automatic when DB comes back. Background events will log errors and enter `FAILED` state if tenacity retries exhaust.
* **Qdrant Loss:** Similar to DB loss; API semantic searches will degrade with an explicit `ServiceError`. Worker embeddings fail and retry.

## 7. Troubleshooting

* **Check Health:** Query `GET /api/v1/health/memory` to quickly pinpoint whether the issue is isolated to Qdrant, Supabase, or the AI Kernel.
* **Invalid States:** If background events stick in `FAILED`, manually update their `embedding_status` to `PENDING` via database or internal dashboard. The worker will automatically resume them.
