import pytest
from unittest.mock import MagicMock
from app.services.context_provider_registry import ContextProviderRegistry
from app.models.enterprise_context import ProviderMetadata
from app.models.enums import ContextSource
from app.models.exceptions import ProviderNotRegisteredError
from app.services.context_freshness import ContextFreshnessPolicy
from app.services.context_retry import ProviderRetryConfig

def test_registry_register_and_get():
    registry = ContextProviderRegistry()
    
    provider_mock = MagicMock()
    metadata = ProviderMetadata(
        source=ContextSource.MEMORY,
        name="Test Memory Provider",
        version="1.0.0"
    )
    
    registry.register(provider=provider_mock, metadata=metadata)
    
    assert registry.is_registered(ContextSource.MEMORY) is True
    assert registry.get(ContextSource.MEMORY) == provider_mock
    
    retrieved_metadata = registry.get_metadata(ContextSource.MEMORY)
    assert retrieved_metadata.name == "Test Memory Provider"
    
    # Defaults should be populated
    freshness = registry.get_freshness_policy(ContextSource.MEMORY)
    assert isinstance(freshness, ContextFreshnessPolicy)
    assert freshness.provider == ContextSource.MEMORY
    
    retry = registry.get_retry_config(ContextSource.MEMORY)
    assert isinstance(retry, ProviderRetryConfig)

def test_registry_get_not_found():
    registry = ContextProviderRegistry()
    
    with pytest.raises(ProviderNotRegisteredError):
        registry.get(ContextSource.TWIN)
        
    with pytest.raises(ProviderNotRegisteredError):
        registry.get_entry(ContextSource.TWIN)

def test_registry_custom_policies():
    registry = ContextProviderRegistry()
    provider_mock = MagicMock()
    metadata = ProviderMetadata(source=ContextSource.GOAL, name="Goal", version="1.0")
    
    custom_freshness = ContextFreshnessPolicy(provider=ContextSource.GOAL, max_age_seconds=60)
    custom_retry = ProviderRetryConfig(max_retries=5)
    
    registry.register(
        provider=provider_mock,
        metadata=metadata,
        freshness_policy=custom_freshness,
        retry_config=custom_retry
    )
    
    assert registry.get_freshness_policy(ContextSource.GOAL).max_age_seconds == 60
    assert registry.get_retry_config(ContextSource.GOAL).max_retries == 5

def test_registry_overwrite():
    registry = ContextProviderRegistry()
    provider_mock1 = MagicMock()
    provider_mock2 = MagicMock()
    
    meta1 = ProviderMetadata(source=ContextSource.PLAN, name="Plan1", version="1")
    meta2 = ProviderMetadata(source=ContextSource.PLAN, name="Plan2", version="2")
    
    registry.register(provider_mock1, meta1)
    registry.register(provider_mock2, meta2)
    
    assert registry.get(ContextSource.PLAN) == provider_mock2

def test_registry_list_methods():
    registry = ContextProviderRegistry()
    
    registry.register(MagicMock(), ProviderMetadata(source=ContextSource.MEMORY, name="M", version="1"))
    registry.register(MagicMock(), ProviderMetadata(source=ContextSource.GOAL, name="G", version="1"))
    
    sources = registry.registered_sources()
    assert len(sources) == 2
    assert ContextSource.MEMORY in sources
    assert ContextSource.GOAL in sources
    
    metadata_list = registry.all_metadata()
    assert len(metadata_list) == 2
    names = [m.name for m in metadata_list]
    assert "M" in names
    assert "G" in names
