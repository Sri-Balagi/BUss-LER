from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.provider import ProviderLifecycleStatus
from app.domain.reasoning.models import ReasoningContext, ReasoningQuery, ReasoningResponse
from app.domain.reasoning.provider import IReasoningProvider


class MockReasoningProvider(IReasoningProvider):
    """
    Mock implementation of a reasoning provider that returns structured Pydantic models.
    Supports status updates for failover testing.
    """

    def __init__(self, priority: int = 1, name: str = "MockReasoningProvider", status: ProviderLifecycleStatus = ProviderLifecycleStatus.READY):
        self._priority = priority
        self._name = name
        self._status = status

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"mock-{self._name}",
            capability_type=CapabilityType.REASONING,
            provider_name=self._name,
            provider_version="1.0.0",
            priority=self._priority,
            supported_features=["text/plain", "application/json"]
        )

    def set_status(self, status: ProviderLifecycleStatus):
        self._status = status

    def get_status(self) -> ProviderLifecycleStatus:
        return self._status

    async def reason(self, context: ReasoningContext, query: ReasoningQuery) -> ReasoningResponse:
        # Mock structured response

        # Check if the twin was passed in the query
        active_twin = query.context_data.get("active_twin", {})

        # Mock payload based on required schema, if any
        payload = {}
        if query.required_schema:
            payload = {"status": "success", "mocked_from_schema": True}
        else:
            payload = {"response": f"Mocked reasoning for: {query.query_text}"}

        return ReasoningResponse(
            payload=payload,
            confidence=0.99,
            evidence=["Mocked Evidence 1", "Mocked Evidence 2"],
            reasoning_trace="Step 1: Read query. Step 2: Return mock.",
            execution_metadata={"tokens_used": 42},
            provider_metadata={"model": self._name, "active_twin": active_twin}
        )
