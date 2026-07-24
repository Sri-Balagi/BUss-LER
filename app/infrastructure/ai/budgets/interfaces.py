"""Interfaces for the Resource Budget System.

Defines the abstract contract for interacting with resource budgets.
This allows the AIKernel to enforce budgets without knowing about
the underlying persistence mechanism (in-memory, Redis, Supabase).
"""

import enum
import sys
from abc import ABC, abstractmethod

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, enum.Enum):
        pass

from typing import Any

from app.infrastructure.ai.budgets.models import TokenBudget


class ResourceBudgetType(StrEnum):
    """The type of resource being constrained."""

    TOKEN = "TOKEN"
    REQUEST = "REQUEST"
    EMBEDDING = "EMBEDDING"
    TOOL_EXECUTION = "TOOL_EXECUTION"
    STORAGE = "STORAGE"
    COST = "COST"


class IResourceBudget(ABC):
    """Abstract interface for resource budget enforcement.

    A budget service is responsible for determining if an entity
    is allowed to consume a certain amount of a resource, and
    recording that consumption when it occurs.
    """

    @property
    @abstractmethod
    def budget_type(self) -> ResourceBudgetType:
        """The type of resource this budget service manages."""
        pass

    @abstractmethod
    async def pre_check(self, entity_id: str, estimated_cost: int = 0) -> None:
        """Check if the entity has sufficient budget before an operation.

        Args:
            entity_id: The entity requesting the resource.
            estimated_cost: The estimated amount of resource needed.

        Raises:
            BudgetExceededError: If the entity has insufficient budget
                                 and the policy is HARD_STOP.
        """
        pass

    @abstractmethod
    async def record_consumption(
        self,
        entity_id: str,
        lifecycle_id: str,
        amount: int,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Record the actual consumption of the resource after an operation.

        Args:
            entity_id: The entity that consumed the resource.
            lifecycle_id: The AI Request Lifecycle ID associated with the usage.
            amount: The actual amount of resource consumed.
            session_id: Optional cognitive session ID.
            **kwargs: Additional resource-specific metadata (e.g., prompt_tokens).
        """
        pass

    @abstractmethod
    async def get_status(self, entity_id: str) -> TokenBudget:
        """Get the current budget status for an entity.

        Args:
            entity_id: The entity to query.

        Returns:
            The current budget configuration and usage.
        """
        pass
