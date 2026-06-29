import pytest
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.permissions import CapabilityPermission
from app.runtime.capabilities.models.resolution import CapabilityResolutionContext
from app.runtime.capabilities.resolution import ExactMatchStrategy, NewestCompatibleStrategy
from app.runtime.capabilities.registry import CapabilityRegistry
from app.runtime.capabilities.factories import TransientCapabilityFactory
from tests.runtime.capabilities.mocks.capabilities import ReadFileCapability
from tests.runtime.capabilities.mocks.adapters import MockFilesystemAdapter

@pytest.fixture
def spec_v1():
    return CapabilitySpecification(
        capability_id="test_cap",
        name="Test",
        category="Test",
        supported_operations=["test"],
        version="1.0.0",
        permissions_required=[]
    )

@pytest.fixture
def spec_v2():
    return CapabilitySpecification(
        capability_id="test_cap",
        name="Test",
        category="Test",
        supported_operations=["test"],
        version="2.0.0",
        permissions_required=[]
    )

@pytest.fixture
def factory():
    return TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)

def test_registry_registration(spec_v1, factory):
    registry = CapabilityRegistry()
    registry.register(spec_v1, factory)
    
    specs = registry.enumerate()
    assert len(specs) == 1
    assert specs[0].capability_id == "test_cap"

def test_registry_unregistration(spec_v1, spec_v2, factory):
    registry = CapabilityRegistry()
    registry.register(spec_v1, factory)
    registry.register(spec_v2, factory)
    
    # Unregister specific version
    registry.unregister("test_cap", version="1.0.0")
    assert len(registry.enumerate()) == 1
    assert registry.enumerate()[0].version == "2.0.0"
    
    # Unregister all
    registry.unregister("test_cap")
    assert len(registry.enumerate()) == 0

def test_exact_match_resolution(spec_v1, spec_v2, factory):
    registry = CapabilityRegistry(default_strategy=ExactMatchStrategy())
    registry.register(spec_v1, factory)
    registry.register(spec_v2, factory)
    
    ctx = CapabilityResolutionContext(capability_id="test_cap", operation="test", requested_version="1.0.0")
    decision = registry.resolve(ctx)
    
    assert decision.selected_specification.version == "1.0.0"
    
def test_newest_compatible_resolution(spec_v1, spec_v2, factory):
    registry = CapabilityRegistry(default_strategy=NewestCompatibleStrategy())
    registry.register(spec_v1, factory)
    registry.register(spec_v2, factory)
    
    ctx = CapabilityResolutionContext(capability_id="test_cap", operation="test")
    decision = registry.resolve(ctx)
    
    assert decision.selected_specification.version == "2.0.0"

def test_resolution_failure():
    registry = CapabilityRegistry()
    ctx = CapabilityResolutionContext(capability_id="missing_cap", operation="test")
    
    with pytest.raises(ValueError, match="No exact match found"):
        registry.resolve(ctx)
