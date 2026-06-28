import pytest

from unittest.mock import MagicMock

from app.models.enterprise_context import ProviderMetadata
from app.models.enums import ContextSource
from app.models.exceptions import ProviderNotRegisteredError
from app.services.context_freshness import ContextFreshnessPolicy
from app.services.context_retry import ProviderRetryConfig
from app.services.context_provider_registry import ContextProviderRegistry, RegistrationEntry

@pytest.fixture
def registry():
    return ContextProviderRegistry()

@pytest.fixture
def mock_provider():
    return MagicMock()

def test_register_and_get(registry, mock_provider):
    metadata = ProviderMetadata(source=ContextSource.GOAL, name="Goal Provider", version="1.0")
    registry.register(mock_provider, metadata)
    
    assert registry.is_registered(ContextSource.GOAL) is True
    assert registry.get(ContextSource.GOAL) == mock_provider
    assert ContextSource.GOAL in registry.registered_sources()

def test_register_overwrite(registry, mock_provider):
    metadata = ProviderMetadata(source=ContextSource.GOAL, name="Goal Provider", version="1.0")
    registry.register(mock_provider, metadata)
    
    mock_provider2 = MagicMock()
    metadata2 = ProviderMetadata(source=ContextSource.GOAL, name="Goal Provider v2", version="2.0")
    registry.register(mock_provider2, metadata2)
    
    assert registry.get(ContextSource.GOAL) == mock_provider2
    assert registry.get_metadata(ContextSource.GOAL).name == "Goal Provider v2"

def test_get_not_registered(registry):
    with pytest.raises(ProviderNotRegisteredError):
        registry.get(ContextSource.INTENT)

def test_get_entry_not_registered(registry):
    with pytest.raises(ProviderNotRegisteredError):
        registry.get_entry(ContextSource.INTENT)

def test_get_all_configs(registry, mock_provider):
    metadata = ProviderMetadata(source=ContextSource.TWIN, name="Twin Provider", version="1.0")
    freshness = ContextFreshnessPolicy(provider=ContextSource.TWIN, ttl_seconds=60)
    retry = ProviderRetryConfig(max_retries=5)
    
    registry.register(mock_provider, metadata, freshness_policy=freshness, retry_config=retry)
    
    assert registry.get_metadata(ContextSource.TWIN) == metadata
    assert registry.get_freshness_policy(ContextSource.TWIN) == freshness
    assert registry.get_retry_config(ContextSource.TWIN) == retry
    
    entry = registry.get_entry(ContextSource.TWIN)
    assert isinstance(entry, RegistrationEntry)
    assert entry.provider == mock_provider

def test_all_metadata(registry, mock_provider):
    meta1 = ProviderMetadata(source=ContextSource.TWIN, name="Twin", version="1.0")
    meta2 = ProviderMetadata(source=ContextSource.GOAL, name="Goal", version="1.0")
    
    registry.register(mock_provider, meta1)
    registry.register(mock_provider, meta2)
    
    all_meta = registry.all_metadata()
    assert len(all_meta) == 2
    assert meta1 in all_meta
    assert meta2 in all_meta
