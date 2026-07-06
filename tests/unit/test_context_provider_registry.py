import sys
from unittest.mock import MagicMock

# Mock structlog due to missing dependency in test environment
if "structlog" not in sys.modules:
    sys.modules["structlog"] = MagicMock()

import pytest
from uuid import UUID

from app.shared.enums import ContextSource
from app.shared.exceptions.errors import ProviderNotRegisteredError
from app.intelligence.intake.situation.enterprise_context import ProviderMetadata, ContextSection
from app.application.context.foundation.context_freshness import ContextFreshnessPolicy
from app.platform.resilience.context_retry import ProviderRetryConfig
from app.application.context.providers.abstract import AbstractContextProvider
from app.application.context.provider_registry import ContextProviderRegistry, DuplicateProviderRegistrationError


class MockProvider(AbstractContextProvider):
    def __init__(self, source: ContextSource):
        self._source = source

    @property
    def source(self) -> ContextSource:
        return self._source

    async def provide(self, ctx, twin_id: UUID, policy) -> ContextSection:
        return ContextSection(source=self._source, items=[], token_estimate=0)

    async def health_check(self) -> dict:
        return {self._source.value: "ok"}


def test_provider_registration_and_lookup():
    registry = ContextProviderRegistry()
    provider = MockProvider(ContextSource.MEMORY)
    metadata = ProviderMetadata(source=ContextSource.MEMORY, name="MemoryProvider", version="1.0")
    
    registry.register(provider, metadata)
    
    assert registry.is_registered(ContextSource.MEMORY)
    assert ContextSource.MEMORY in registry
    assert len(registry) == 1
    
    # lookup
    retrieved_provider = registry.get(ContextSource.MEMORY)
    assert retrieved_provider is provider


def test_duplicate_registration_rejection():
    registry = ContextProviderRegistry()
    provider = MockProvider(ContextSource.MEMORY)
    metadata = ProviderMetadata(source=ContextSource.MEMORY, name="MemoryProvider", version="1.0")
    
    registry.register(provider, metadata)
    
    with pytest.raises(DuplicateProviderRegistrationError):
        registry.register(provider, metadata)


def test_unregister():
    registry = ContextProviderRegistry()
    provider = MockProvider(ContextSource.TWIN)
    metadata = ProviderMetadata(source=ContextSource.TWIN, name="TwinProvider", version="1.0")
    
    registry.register(provider, metadata)
    assert ContextSource.TWIN in registry
    
    registry.unregister(ContextSource.TWIN)
    assert ContextSource.TWIN not in registry
    assert len(registry) == 0


def test_unregister_not_registered():
    registry = ContextProviderRegistry()
    with pytest.raises(ProviderNotRegisteredError):
        registry.unregister(ContextSource.GOAL)


def test_metadata_and_config_retrieval():
    registry = ContextProviderRegistry()
    provider = MockProvider(ContextSource.PLAN)
    metadata = ProviderMetadata(source=ContextSource.PLAN, name="PlanProvider", version="1.0")
    freshness = ContextFreshnessPolicy(provider=ContextSource.PLAN, max_age_seconds=120)
    retry = ProviderRetryConfig(max_retries=5)
    
    registry.register(provider, metadata, freshness, retry)
    
    assert registry.get_metadata(ContextSource.PLAN) is metadata
    assert registry.get_freshness_policy(ContextSource.PLAN) is freshness
    assert registry.get_retry_config(ContextSource.PLAN) is retry
    
    entry = registry.get_entry(ContextSource.PLAN)
    assert entry.provider is provider
    assert entry.metadata is metadata


def test_iteration_and_length():
    registry = ContextProviderRegistry()
    p1 = MockProvider(ContextSource.MEMORY)
    p2 = MockProvider(ContextSource.TWIN)
    p3 = MockProvider(ContextSource.GOAL)
    
    registry.register(p1, ProviderMetadata(source=ContextSource.MEMORY, name="M", version="1.0"))
    registry.register(p2, ProviderMetadata(source=ContextSource.TWIN, name="T", version="1.0"))
    registry.register(p3, ProviderMetadata(source=ContextSource.GOAL, name="G", version="1.0"))
    
    assert len(registry) == 3
    sources = registry.registered_sources()
    assert set(sources) == {ContextSource.MEMORY, ContextSource.TWIN, ContextSource.GOAL}
    
    # Deterministic iteration test
    # Should iterate alphabetically by source.value (goal, memory, twin)
    iterated_sources = [entry.metadata.source for entry in registry]
    expected_order = sorted([ContextSource.MEMORY, ContextSource.TWIN, ContextSource.GOAL], key=lambda s: s.value)
    
    assert iterated_sources == expected_order


def test_failure_cases():
    registry = ContextProviderRegistry()
    
    with pytest.raises(ProviderNotRegisteredError):
        registry.get(ContextSource.EXTERNAL)
        
    with pytest.raises(ProviderNotRegisteredError):
        registry.get_entry(ContextSource.EXTERNAL)

    with pytest.raises(ProviderNotRegisteredError):
        registry.get_metadata(ContextSource.EXTERNAL)
        
    with pytest.raises(ProviderNotRegisteredError):
        registry.get_freshness_policy(ContextSource.EXTERNAL)
        
    with pytest.raises(ProviderNotRegisteredError):
        registry.get_retry_config(ContextSource.EXTERNAL)
