import pytest

from app.models.enterprise_context import ProviderDependency
from app.models.enums import ContextSource
from app.models.exceptions import ContextDependencyCycleError
from app.services.context_dependency_graph import ContextDependencyGraph, build_default_dependency_graph

def test_graph_independent_providers():
    graph = ContextDependencyGraph()
    graph.register(ProviderDependency(provider=ContextSource.GOAL, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.INTENT, depends_on=[]))
    
    plan = graph.resolve([ContextSource.GOAL, ContextSource.INTENT])
    assert plan.total_providers == 2
    # Since they are independent, they should both be in the first batch
    assert len(plan.batches) == 1
    assert set(plan.batches[0]) == {ContextSource.GOAL, ContextSource.INTENT}

def test_graph_linear_dependencies():
    graph = ContextDependencyGraph()
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN]))
    graph.register(ProviderDependency(provider=ContextSource.BUSINESS_STATE, depends_on=[ContextSource.CONVERSATION]))
    
    plan = graph.resolve([ContextSource.TWIN, ContextSource.CONVERSATION, ContextSource.BUSINESS_STATE])
    assert plan.total_providers == 3
    assert len(plan.batches) == 3
    assert plan.batches[0] == [ContextSource.TWIN]
    assert plan.batches[1] == [ContextSource.CONVERSATION]
    assert plan.batches[2] == [ContextSource.BUSINESS_STATE]

def test_graph_partial_resolution():
    graph = ContextDependencyGraph()
    # Register TWIN and CONVERSATION, but only resolve CONVERSATION
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN]))
    
    # If we only request CONVERSATION, it shouldn't wait for TWIN in the active set
    plan = graph.resolve([ContextSource.CONVERSATION])
    assert plan.total_providers == 1
    assert len(plan.batches) == 1
    assert plan.batches[0] == [ContextSource.CONVERSATION]

def test_graph_cycle_detection_on_register():
    graph = ContextDependencyGraph()
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[ContextSource.CONVERSATION]))
    with pytest.raises(ContextDependencyCycleError) as exc:
        graph.register(ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN]))
    
    assert "twin" in str(exc.value)
    assert "conversation" in str(exc.value)

def test_graph_complex_cycle_detection_on_register():
    graph = ContextDependencyGraph()
    graph.register(ProviderDependency(provider=ContextSource.GOAL, depends_on=[ContextSource.PLAN]))
    graph.register(ProviderDependency(provider=ContextSource.PLAN, depends_on=[ContextSource.INTENT]))
    with pytest.raises(ContextDependencyCycleError):
        graph.register(ProviderDependency(provider=ContextSource.INTENT, depends_on=[ContextSource.GOAL]))

def test_graph_empty_providers():
    graph = ContextDependencyGraph()
    plan = graph.resolve([])
    assert plan.total_providers == 0
    assert len(plan.batches) == 0

def test_graph_empty_detection():
    graph = ContextDependencyGraph()
    # Should just return none
    graph._detect_cycle()

def test_build_default_dependency_graph():
    graph = build_default_dependency_graph()
    plan = graph.resolve([ContextSource.TWIN, ContextSource.CONVERSATION, ContextSource.BUSINESS_STATE, ContextSource.GOAL])
    
    assert plan.total_providers == 4
    # TWIN and GOAL are independent
    # CONVERSATION and BUSINESS_STATE depend on TWIN
    assert len(plan.batches) == 2
    assert set(plan.batches[0]) == {ContextSource.TWIN, ContextSource.GOAL}
    assert set(plan.batches[1]) == {ContextSource.CONVERSATION, ContextSource.BUSINESS_STATE}

def test_resolve_cycle():
    # Hack the graph to have a cycle without triggering register detection
    graph = ContextDependencyGraph()
    graph._dependencies[ContextSource.GOAL] = {ContextSource.PLAN}
    graph._dependencies[ContextSource.PLAN] = {ContextSource.GOAL}
    
    with pytest.raises(ContextDependencyCycleError) as exc:
        graph.resolve([ContextSource.GOAL, ContextSource.PLAN])
    assert "goal" in str(exc.value) or "plan" in str(exc.value)
