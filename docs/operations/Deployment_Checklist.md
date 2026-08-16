# BizOS Memory Engine Deployment Checklist

Use this checklist during production rollouts to ensure a safe and validated release.

## 1. Pre-Deployment
- [ ] Merge target code into the production release branch.
- [ ] Confirm all GitHub Actions / CI tests are passing (coverage >95%).
- [ ] Identify if new database migrations exist in `migrations/`.
- [ ] Validate environment configuration (`.env`) is safely injected in the deployment platform.
- [ ] Ensure `SUPABASE_KEY` and `GEMINI_API_KEY` are valid and not expired.

## 2. Deployment
- [ ] Execute Supabase SQL migrations from `migrations/` in sequential order via the Supabase UI or CLI.
- [ ] Reload Supabase Schema Cache.
- [ ] Deploy Qdrant vector database (ensure volume mounts persist data).
- [ ] Deploy the Background Processing Worker container.
- [ ] Deploy the FastAPI Web application container.

## 3. Post-Deployment
- [ ] Call `GET /api/v1/health` and verify HTTP 200.
- [ ] Call `GET /api/v1/health/memory` and verify all subsystems report `"status": "healthy"`.
- [ ] Check structured logs for the first 5 minutes to ensure no continuous restarts or configuration tracebacks.
- [ ] Submit a test memory via `POST /api/v1/twins/{twin_id}/memory` and verify the background worker completes processing without exceptions.

## 4. Rollback
If the deployment introduces critical failures (API 500s or Worker crashes):
- [ ] Revert the Docker image tag to the previous stable build.
- [ ] Restart the Worker and API containers.
- [ ] **Data Rollback:** If a migration was destructive (avoid this architecturally), manually reverse the SQL DDL operations. BizOS strictly uses additive schemas, so code rollback alone is usually sufficient.

## 5. Incident Recovery
- [ ] If Qdrant goes offline, restart the container and review `Operations_Runbook.md`.
- [ ] If events pile up in `FAILED` state, reset them to `PENDING` via DB and verify the Worker picks them up on restart.

## 6. Maintenance
- [ ] Rotate API keys if they are exposed.
- [ ] Review performance baselines periodically.
- [ ] Monitor vector database disk usage over time.
