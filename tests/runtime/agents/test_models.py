import pytest
from pydantic import ValidationError
from app.runtime.agents.permissions import AgentPermission
from app.runtime.agents.specification import AgentSpecification, ExecutionType
from app.runtime.agents.manifest import AgentManifest
from app.runtime.agents.results import AgentResult, AgentStatus
from app.runtime.agents.health import AgentHealth

def test_agent_specification_valid():
    spec = AgentSpecification(
        identity="finance-bot",
        capabilities=["forecast"],
        permissions=[AgentPermission.READ_MEMORY],
        execution_support=ExecutionType.SYNCHRONOUS
    )
    assert spec.identity == "finance-bot"
    assert spec.capabilities == ["forecast"]
    assert spec.permissions == [AgentPermission.READ_MEMORY]
    assert spec.execution_support == ExecutionType.SYNCHRONOUS

def test_agent_specification_invalid():
    with pytest.raises(ValidationError):
        # Missing identity
        AgentSpecification(capabilities=["forecast"])

def test_agent_manifest_valid():
    manifest = AgentManifest(
        version="1.0.0",
        deployment_source="local",
        author="BizOS Team"
    )
    assert manifest.version == "1.0.0"
    assert manifest.author == "BizOS Team"

def test_agent_result_valid():
    result = AgentResult(
        status=AgentStatus.SUCCESS,
        outputs={"revenue": 1000},
        metrics={"duration_ms": 15.5}
    )
    assert result.status == AgentStatus.SUCCESS
    assert result.outputs["revenue"] == 1000
    assert result.metrics["duration_ms"] == 15.5

def test_agent_health_defaults():
    health = AgentHealth()
    assert health.success_rate == 1.0
    assert health.average_latency_ms == 0.0
    assert health.recent_failures == 0
    assert health.is_available is True
    assert health.in_cooldown is False
