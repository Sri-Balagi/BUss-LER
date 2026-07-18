import pytest
import asyncio
from uuid import uuid4

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.twin.service import DigitalTwinService
from app.application.twin.orchestrator import TwinSyncOrchestrator
from app.bootstrap.container import build_container, Container


@pytest.fixture
def container():
    return build_container()


@pytest.mark.asyncio
async def test_twin_capability_resolution(container: Container):
    registry = container.resolve(ICapabilityRegistry)
    provider = registry.resolve_provider(CapabilityType.TWIN)
    
    assert provider is not None
    assert provider.get_metadata().provider_name == "InMemoryTwinProvider"
    assert provider.get_metadata().priority == 1


@pytest.mark.asyncio
async def test_twin_sync_orchestrator(container: Container):
    orchestrator = container.resolve(TwinSyncOrchestrator)
    service = container.resolve(DigitalTwinService)
    
    tenant_id = uuid4()
    entity_id = uuid4()
    context = IntelligenceContext(tenant_id=tenant_id)
    
    new_props = {"department": "Engineering", "budget": 1000000}
    
    # Fire orchestrator event (simulating BKG update)
    await orchestrator.handle_bkg_entity_updated(context, entity_id, new_props)
    
    # Assert twin was created and updated in real-time
    twin = await service.get_twin(context, entity_id)
    
    assert twin is not None
    assert twin.entity_id == entity_id
    assert twin.tenant_id == tenant_id
    assert twin.properties["department"] == "Engineering"
    assert twin.properties["budget"] == 1000000
    assert twin.version == 2
    
    # Fire another update
    await orchestrator.handle_bkg_entity_updated(context, entity_id, {"budget": 1200000})
    
    twin_updated = await service.get_twin(context, entity_id)
    assert twin_updated is not None
    assert twin_updated.properties["budget"] == 1200000
    assert twin_updated.version == 3
