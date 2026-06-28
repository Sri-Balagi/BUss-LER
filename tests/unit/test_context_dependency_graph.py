import pytest
from app.services.context_dependency_graph import ContextDependencyGraph
from app.models.enterprise_context import ProviderDependency
from app.models.enums import ContextSource
from app.models.exceptions import ContextDependencyCycleError

def test_graph_registration_and_resolution():
    graph = ContextDependencyGraph()
    
    graph.register(ProviderDependency(
        provider=ContextSource.TWIN,
        depends_on=[]
    ))
    graph.register(ProviderDependency(
        provider=ContextSource.CONVERSATION,
        depends_on=[ContextSource.TWIN]
    ))
    
    plan = graph.resolve([ContextSource.TWIN, ContextSource.CONVERSATION])
    
    assert plan.total_providers == 2
    assert len(plan.batches) == 2
    assert plan.batches[0] == [ContextSource.TWIN]
    assert plan.batches[1] == [ContextSource.CONVERSATION]

def test_graph_cycle_detection_on_register():
    graph = ContextDependencyGraph()
    
    graph.register(ProviderDependency(
        provider=ContextSource.TWIN,
        depends_on=[ContextSource.CONVERSATION]
    ))
    
    with pytest.raises(ContextDependencyCycleError):
        graph.register(ProviderDependency(
            provider=ContextSource.CONVERSATION,
            depends_on=[ContextSource.TWIN]
        ))

def test_graph_unrelated_providers():
    graph = ContextDependencyGraph()
    
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.MEMORY, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.GOAL, depends_on=[]))
    
    plan = graph.resolve([ContextSource.TWIN, ContextSource.MEMORY, ContextSource.GOAL])
    
    assert plan.total_providers == 3
    assert len(plan.batches) == 1
    
    batch = plan.batches[0]
    assert ContextSource.TWIN in batch
    assert ContextSource.MEMORY in batch
    assert ContextSource.GOAL in batch

def test_graph_complex_dependencies():
    graph = ContextDependencyGraph()
    
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.BUSINESS_STATE, depends_on=[ContextSource.TWIN]))
    graph.register(ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN, ContextSource.BUSINESS_STATE]))
    graph.register(ProviderDependency(provider=ContextSource.MEMORY, depends_on=[]))
    
    plan = graph.resolve([
        ContextSource.TWIN,
        ContextSource.BUSINESS_STATE,
        ContextSource.CONVERSATION,
        ContextSource.MEMORY
    ])
    
    assert plan.total_providers == 4
    # Batch 0: TWIN, MEMORY
    # Batch 1: BUSINESS_STATE
    # Batch 2: CONVERSATION
    assert len(plan.batches) == 3
    assert ContextSource.TWIN in plan.batches[0]
    assert ContextSource.MEMORY in plan.batches[0]
    assert plan.batches[1] == [ContextSource.BUSINESS_STATE]
    assert plan.batches[2] == [ContextSource.CONVERSATION]

def test_graph_partial_resolution():
    graph = ContextDependencyGraph()
    
    graph.register(ProviderDependency(provider=ContextSource.TWIN, depends_on=[]))
    graph.register(ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN]))
    
    # Resolve only CONVERSATION without TWIN requested
    plan = graph.resolve([ContextSource.CONVERSATION])
    
    assert plan.total_providers == 1
    assert len(plan.batches) == 1
    assert plan.batches[0] == [ContextSource.CONVERSATION]
