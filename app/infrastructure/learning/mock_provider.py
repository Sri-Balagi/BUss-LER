import asyncio
import time
from typing import List

from app.domain.learning.provider import ILearningProvider
from app.domain.learning.models import LearningContext, LearningResult, LearningMetrics
from app.domain.intelligence.provider import ProviderLifecycleStatus
from app.domain.cognition.models import ReflectionFeedback
from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType


class MockLearningProvider(ILearningProvider):
    """
    Mock implementation of ILearningProvider for deterministic testing.
    """

    def __init__(self, priority: int = 1, name: str = "MockLearningProvider"):
        self._priority = priority
        self._name = name
        self._status = ProviderLifecycleStatus.READY

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"learning-{self._name.lower()}",
            capability_type=CapabilityType.LEARNING,
            provider_name=self._name,
            provider_version="1.0.0",
            priority=self._priority,
            supported_features=["mock_consolidation"]
        )

    def set_status(self, status: ProviderLifecycleStatus) -> None:
        self._status = status
        
    def get_status(self) -> ProviderLifecycleStatus:
        return self._status

    @property
    def status(self) -> ProviderLifecycleStatus:
        return self._status

    async def check_health(self) -> bool:
        return self._status == ProviderLifecycleStatus.READY

    async def consolidate_knowledge(self, context: LearningContext) -> LearningResult:
        """
        Simulates extracting and consolidating knowledge.
        """
        start_time = time.time()
        
        # Simulate async work
        await asyncio.sleep(0.01)
        
        # Determine items consolidated based on feedback
        extracted_items = []
        if context.feedback and context.feedback == ReflectionFeedback.IS_COMPLETE:
            extracted_items = ["rule_1", "rule_2"]
        
        consolidation_time_ms = (time.time() - start_time) * 1000.0

        metrics = LearningMetrics(
            extraction_time_ms=consolidation_time_ms * 0.4,
            consolidation_time_ms=consolidation_time_ms * 0.6,
            items_consolidated=len(extracted_items)
        )

        return LearningResult(
            success=True,
            metrics=metrics,
            consolidated_items=extracted_items,
            errors=[],
            correlation_id=context.correlation_id
        )
