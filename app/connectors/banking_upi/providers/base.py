"""BizOS Financial Provider Strategy Interface — IFinancialAuthProvider"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.domain.shared.context import ExecutionContext


class DiscoveredAccount(BaseModel):
    account_id: str
    account_name: str
    account_type: str  # e.g., SAVINGS, CHECKING, UPI_VPA, BUSINESS
    currency: str = "USD"
    masked_identifier: str  # e.g., "****1234" or "user@vpa"
    provider_id: str
    is_selected: bool = False


class IFinancialAuthProvider(ABC):
    """Abstract Strategy interface for all Financial & Payment Authentication Providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_capabilities(self) -> List[str]:
        """Dynamic list of capabilities supported by this financial provider."""
        pass

    @abstractmethod
    async def initiate_auth(self, user_id: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Generate official provider authorization URL or challenge (No manual secret entry)."""
        pass

    @abstractmethod
    async def complete_auth(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Exchange provider authorization payload for encrypted tokens."""
        pass

    @abstractmethod
    async def discover_accounts(self, access_token: str) -> List[DiscoveredAccount]:
        """Auto-discover available accounts linked to provider authorization."""
        pass

    @abstractmethod
    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute financial action enforcing SIMULATION, DRY_RUN, and PRODUCTION execution modes."""
        pass
