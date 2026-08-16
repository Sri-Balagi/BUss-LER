"""BizOS Financial Provider Registry

Responsible for dynamic discovery, registration, lookup, and capability resolution
of financial authentication providers.
"""

from typing import Dict, List, Optional
from app.connectors.banking_upi.providers.base import IFinancialAuthProvider
from app.connectors.banking_upi.providers.open_banking import OpenBankingProvider
from app.connectors.banking_upi.providers.account_aggregator import AccountAggregatorProvider
from app.connectors.banking_upi.providers.stripe_connect import StripeProvider
from app.connectors.banking_upi.providers.razorpay import RazorpayProvider


class FinancialProviderRegistry:
    """Central registry for discovering and resolving financial providers dynamically."""

    def __init__(self) -> None:
        self._providers: Dict[str, IFinancialAuthProvider] = {}
        # Auto-register standard built-in providers
        self.register_provider(OpenBankingProvider())
        self.register_provider(AccountAggregatorProvider())
        self.register_provider(StripeProvider())
        self.register_provider(RazorpayProvider())

    def register_provider(self, provider: IFinancialAuthProvider) -> None:
        """Register a financial provider strategy plugin."""
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[IFinancialAuthProvider]:
        """Resolve a financial provider plugin by provider_id."""
        return self._providers.get(provider_id)

    def list_providers(self) -> List[Dict[str, str]]:
        """List all registered providers with display names."""
        return [
            {
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "capabilities": p.provider_capabilities,
            }
            for p in self._providers.values()
        ]

    def get_provider_capabilities(self, provider_id: str) -> List[str]:
        """Discover capabilities supported by a specific provider."""
        provider = self.get_provider(provider_id)
        if provider:
            return provider.provider_capabilities
        return []
