from app.runtime.agents.capability import Capability
from app.runtime.agents.interfaces import IAgentFactory
from app.runtime.agents.monitor import AgentHealthMonitor
from app.runtime.agents.permissions import AgentPermission
from app.runtime.agents.ranking import HealthRankingStrategy
from app.runtime.agents.registry import AgentRegistry, ResolutionContext
from app.runtime.agents.specification import AgentSpecification


class MockFactory(IAgentFactory):
    def create_agent(self, spec):
        pass

    def release_agent(self, agent):
        pass


def setup_registry():
    monitor = AgentHealthMonitor()
    strategy = HealthRankingStrategy()
    registry = AgentRegistry(monitor, strategy)
    return registry, monitor


def test_registry_resolution_success():
    registry, monitor = setup_registry()

    spec = AgentSpecification(
        identity="agent-1", capabilities=["write_code"], permissions=[AgentPermission.WRITE_MEMORY]
    )
    factory = MockFactory()
    registry.register(spec, factory)

    context = ResolutionContext(
        requested_capability=Capability(capability_id="write_code"),
        required_permissions={AgentPermission.WRITE_MEMORY},
    )

    decision = registry.resolve(context)

    assert decision.selected_factory is factory
    assert decision.selected_specification is spec
    assert decision.ranking_score.overall_score == 1.0
    assert len(decision.fallback_candidates) == 0
    assert decision.trace.evaluated_candidates == 1


def test_registry_resolution_fallback():
    registry, monitor = setup_registry()

    # Best agent
    spec1 = AgentSpecification(identity="agent-best", capabilities=["write_code"])
    # Fallback agent
    spec2 = AgentSpecification(identity="agent-fallback", capabilities=["write_code"])

    factory1 = MockFactory()
    factory2 = MockFactory()

    registry.register(spec1, factory1)
    registry.register(spec2, factory2)

    # Simulate health degradation for best agent
    monitor.record_success("agent-best", 100.0)
    monitor.record_failure("agent-best")

    context = ResolutionContext(requested_capability=Capability(capability_id="write_code"))
    decision = registry.resolve(context)

    # Factory 2 should win because agent-best has lower score
    assert decision.selected_factory is factory2
    assert decision.selected_specification is spec2
    assert decision.ranking_score.overall_score == 1.0

    assert len(decision.fallback_candidates) == 1
    assert decision.fallback_candidates[0] is spec1
    assert decision.trace.evaluated_candidates == 2


def test_registry_resolution_no_candidates():
    registry, _ = setup_registry()

    context = ResolutionContext(requested_capability=Capability(capability_id="unknown"))
    decision = registry.resolve(context)

    assert decision.selected_factory is None
    assert decision.selection_reason == "No valid candidates found"
