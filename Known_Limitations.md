# Known Limitations

BizOS is an evolving AI Operating System. The following limitations are acknowledged in the current `v2.0.0` architecture:

## Security & Access Control
* **Authentication Deferred:** There is currently no API authentication mechanism (e.g., JWT, OAuth). The API is completely open by default and relies on network-level security.
* **Authorization Deferred:** Multi-tenant isolation is enforced via `twin_id` scoping in the repositories, but explicit RBAC (Role-Based Access Control) is not yet implemented.

## Infrastructure
* **Distributed Task Queues Planned:** The current `BackgroundTasksDispatcher` utilizes `asyncio` background tasks. For multi-node horizontal scaling, a distributed queue like Celery, RabbitMQ, or Redis RQ is planned.
* **Monitoring Dashboards Planned:** While `/health` endpoints and structured logs exist, a visual monitoring dashboard (e.g., Grafana/Prometheus) is not included.

## Upstream Dependencies
* **Gemini Free-Tier Rate Limits:** Heavy background processing of memory vectors may trigger HTTP 429 errors on the free tier of the Gemini API. The `tenacity` retry logic handles this gracefully, but processing latency will spike.

## Future Capabilities
* **Intent Engine:** Proactive agentic behavior and reasoning are scheduled to begin in Milestone 3. The current system records and searches memory but does not act autonomously.
