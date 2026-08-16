# BizOS Deployment Guide

This guide details the steps to deploy BizOS v4.0.0 (Enterprise Context Engine) into a clean production environment.

## Prerequisites
- Python >= 3.12 (or Docker)
- PostgreSQL (via Supabase) with pgvector enabled
- Qdrant Vector Database
- Redis (Optional, for caching layer overrides)

## Installation

```bash
# Clone the repository
git clone https://github.com/organization/bizos.git
cd bizos

# Install via uv
pip install uv
uv venv
uv pip install -e .
```

## Configuration (Environment Variables)

Create a `.env` file at the root of the project:

```env
# Server
ENVIRONMENT=production
LOG_LEVEL=INFO

# Supabase (PostgreSQL)
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-service-role-key>

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# LLM Providers (Mocked for M4, required for M5)
OPENAI_API_KEY=
GEMINI_API_KEY=
```

## Migrations

BizOS relies on Supabase CLI or native Alembic/SQL scripts for schema migrations.
To run the latest `004_context_engine` migration:
```bash
# Example if using supabase CLI
supabase db push
```

## Startup

Start the BizOS API Gateway (FastAPI):
```bash
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000 --workers 4
```

## Shutdown
Graceful shutdown is supported by Uvicorn. Send `SIGTERM` to the master process. It will gracefully close database connections, drain the event bus, and exit.

## Rollback
If deployment fails, rollback to `v3.0.0` involves:
1. Revert Git tag/Docker image to `v3.0.0`.
2. Downgrade database schema if breaking changes were applied (v4 requires backwards-compatible columns, but verify `003_rollback.sql`).
3. Restart application servers.

## Health Verification
After startup, verify the deployment:
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "version": "4.0.0"}
```
