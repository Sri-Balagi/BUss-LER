from app.domain.cognition.models import IAgentImplementation
from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.provider import ProviderLifecycleStatus


class MockAgentImplementation(IAgentImplementation):
    """
    Mock agent persona provider for testing execution loops and failovers.
    """

    def __init__(self, priority: int = 1, name: str = "MockAgent"):
        self._priority = priority
        self._name = name
        self._status = ProviderLifecycleStatus.READY

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"agent-{self._name.lower()}",
            capability_type=CapabilityType.AGENT,  # Assuming AGENT is added to CapabilityType
            provider_name=self._name,
            provider_version="1.0.0",
            priority=self._priority,
            supported_features=["mock_cognition"]
        )

    def set_status(self, status: ProviderLifecycleStatus) -> None:
        self._status = status

    def get_status(self) -> ProviderLifecycleStatus:
        return self._status
