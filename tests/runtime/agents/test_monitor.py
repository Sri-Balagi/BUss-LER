from app.runtime.agents.monitor import AgentHealthMonitor


def test_health_monitor_success():
    monitor = AgentHealthMonitor()

    # Record success
    monitor.record_success("agent-1", duration_ms=100.0)
    health = monitor.get_health("agent-1")

    assert health.success_rate == 1.0
    assert health.average_latency_ms == 100.0
    assert health.recent_failures == 0
    assert health.is_available is True

    # Record another success
    monitor.record_success("agent-1", duration_ms=200.0)
    health = monitor.get_health("agent-1")

    assert health.success_rate == 1.0
    assert health.average_latency_ms == 150.0


def test_health_monitor_failure_cooldown():
    monitor = AgentHealthMonitor()

    for _ in range(3):
        monitor.record_failure("agent-2")

    health = monitor.get_health("agent-2")

    assert health.success_rate == 0.0
    assert health.recent_failures == 3
    assert health.in_cooldown is True


def test_health_monitor_default_health():
    monitor = AgentHealthMonitor()
    health = monitor.get_health("unknown")
    assert health.success_rate == 1.0
    assert health.is_available is True
