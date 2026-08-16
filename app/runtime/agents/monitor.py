from app.runtime.agents.health import AgentHealth


class AgentHealthMonitor:
    """
    Passive advisory telemetry for agent health.
    Does not make routing decisions.
    """

    def __init__(self):
        self._health_store: dict[str, AgentHealth] = {}
        # We also might track running counts, total durations etc.
        self._stats: dict[str, dict] = {}

    def _ensure_tracked(self, agent_id: str) -> None:
        if agent_id not in self._health_store:
            self._health_store[agent_id] = AgentHealth()
            self._stats[agent_id] = {"total_executions": 0, "total_duration_ms": 0.0}

    def record_success(self, agent_id: str, duration_ms: float) -> None:
        """Advisory signal that an execution succeeded."""
        self._ensure_tracked(agent_id)

        health = self._health_store[agent_id]
        stats = self._stats[agent_id]

        stats["total_executions"] += 1
        stats["total_duration_ms"] += duration_ms

        health.average_latency_ms = stats["total_duration_ms"] / stats["total_executions"]
        health.recent_failures = 0
        health.in_cooldown = False

        # Simple success rate decay (or cumulative). Here we'll do cumulative for simplicity.
        # But wait, success_rate is float (0 to 1). Let's say we have failures.
        # we'd track total_successes.
        if "total_successes" not in stats:
            stats["total_successes"] = 0
        stats["total_successes"] += 1

        health.success_rate = stats["total_successes"] / stats["total_executions"]

    def record_failure(self, agent_id: str) -> None:
        """Advisory signal that an execution failed."""
        self._ensure_tracked(agent_id)

        health = self._health_store[agent_id]
        stats = self._stats[agent_id]

        stats["total_executions"] += 1
        if "total_successes" not in stats:
            stats["total_successes"] = 0

        health.recent_failures += 1
        health.success_rate = stats["total_successes"] / stats["total_executions"]

        # Advisory cooldown flag if too many recent failures
        if health.recent_failures >= 3:
            health.in_cooldown = True

    def get_health(self, agent_id: str) -> AgentHealth:
        """Retrieves advisory health."""
        if agent_id not in self._health_store:
            return AgentHealth()  # Default healthy state
        return self._health_store[agent_id]
