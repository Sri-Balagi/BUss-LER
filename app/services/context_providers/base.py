"""AbstractContextProvider — base interface for all context providers.

All providers must implement:
  - provide(ctx, twin_id, policy) → ContextSection
  - health_check() → dict
"""

from abc import ABC, abstractmethod
from uuid import UUID


class AbstractContextProvider(ABC):
    """Base contract for all context source providers.

    Each provider is responsible for fetching data from exactly one cognitive
    subsystem and returning a typed ContextSection.

    Providers must never:
      - Access databases directly
      - Call the AI Kernel
      - Call other providers
      - Hold mutable shared state
    """

    @abstractmethod
    async def provide(
        self,
        ctx,                  # OperationContext
        twin_id: UUID,
        policy,               # ContextPolicy
    ):
        """Fetch context from the underlying service and return a ContextSection."""
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Verify that the provider's underlying service is reachable.

        Returns a dict with at least one key: the provider name → 'ok' | 'error'.
        Follows the same pattern as AbstractMemoryRepository.health_check()
        and AIKernel.health_check().
        """
        pass
