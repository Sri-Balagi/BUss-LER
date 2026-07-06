"""AbstractContextProvider — base interface for all context providers.

All providers must implement:
  - source (property) → ContextSource
  - provide(ctx, twin_id, policy) → ContextSection
  - health_check() → dict
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.shared.enums import ContextSource
from app.intelligence.intake.situation.enterprise_context import ContextSection
from app.application.context.foundation.context_policies import ContextPolicy


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

    @property
    @abstractmethod
    def source(self) -> ContextSource:
        """The specific ContextSource this provider is responsible for."""
        pass

    @abstractmethod
    async def provide(
        self,
        ctx: Any,  # OperationContext
        twin_id: UUID,
        policy: ContextPolicy,
    ) -> ContextSection:
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
