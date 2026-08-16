import asyncio
from uuid import uuid4

import pytest

from app.application.intelligence.kernel import IntelligenceKernel
from app.application.learning.service import LearningService
from app.bootstrap.container import Container, build_container, reset_container_for_testing
from app.domain.cognition.events import LearningRequested
from app.domain.cognition.models import ReflectionFeedback
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry
from app.domain.learning.events import (
    KnowledgeConsolidated,
    KnowledgeExtracted,
    LearningCompleted,
    LearningStarted,
)


@pytest.fixture
def container():
    reset_container_for_testing()
    c = build_container()

    c.resolve("learning_registry_initializer")

    yield c
    reset_container_for_testing()


@pytest.mark.asyncio
async def test_learning_capability_resolution(container: Container):
    """Test that the learning capability is registered in the registry."""
    registry = container.resolve(ICapabilityRegistry)

    providers = registry.resolve_all_providers(CapabilityType.LEARNING)
    assert len(providers) >= 1

    provider = registry.resolve_provider(CapabilityType.LEARNING)
    assert provider is not None
    assert provider.get_metadata().provider_name == "MockLearningProvider"


@pytest.mark.asyncio
async def test_learning_consolidation_pipeline(container: Container):
    """Test that the LearningService correctly handles the learning pipeline."""
    service = container.resolve(LearningService)
    kernel = container.resolve(IntelligenceKernel)
    event_router = kernel.event_router

    # Setup mock event handler to capture events
    captured_events = []

    original_publish = event_router.publish

    async def mock_publish(event):
        captured_events.append(event)
        await original_publish(event)

    event_router.publish = mock_publish

    # Simulate a successful learning request
    event = LearningRequested(
        event_id=str(uuid4()),
        correlation_id=str(uuid4()),
        agent_id=uuid4(),
        tenant_id=None,
        iteration=1,
        feedback=ReflectionFeedback.IS_COMPLETE
    )

    result = await service.handle_learning_requested(event)

    assert result is not None
    assert result.success is True
    assert result.metrics.items_consolidated == 2
    assert len(result.consolidated_items) == 2

    # Verify events
    event_types = [type(e).__name__ for e in captured_events]
    assert "LearningStarted" in event_types
    assert "KnowledgeExtracted" in event_types
    assert "KnowledgeConsolidated" in event_types
    assert "LearningCompleted" in event_types

    completed_event = next(e for e in captured_events if type(e).__name__ == "LearningCompleted")
    assert completed_event.result.metrics.items_consolidated == 2
