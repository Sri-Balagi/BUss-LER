"""Account Aggregator Protocol Strategy Driver"""

from typing import Any, Dict, List
from app.connectors.banking_upi.providers.base import IFinancialAuthProvider, DiscoveredAccount
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


class AccountAggregatorProvider(IFinancialAuthProvider):
    @property
    def provider_id(self) -> str:
        return "account_aggregator"

    @property
    def display_name(self) -> str:
        return "Account Aggregator Framework"

    @property
    def provider_capabilities(self) -> List[str]:
        return ["read_accounts", "read_balance", "read_statements", "fetch_financial_insights"]

    async def initiate_auth(self, user_id: str, options: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {
            "status": "INITIATED",
            "provider_id": self.provider_id,
            "auth_url": f"https://api.accountaggregator.org/consent/create?user_handle={user_id}@aa",
            "requires_manual_credentials": False,
        }

    async def complete_auth(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        consent_handle = auth_payload.get("consent_handle", "aa_handle_123")
        return {
            "status": "SUCCESS",
            "provider_id": self.provider_id,
            "access_token": f"aa_session_{consent_handle}",
            "expires_in": 7200,
        }

    async def discover_accounts(self, access_token: str) -> List[DiscoveredAccount]:
        return [
            DiscoveredAccount(
                account_id="aa_fip_101",
                account_name="HDFC Operating Account",
                account_type="BUSINESS",
                currency="INR",
                masked_identifier="****5432",
                provider_id=self.provider_id,
                is_selected=True,
            ),
            DiscoveredAccount(
                account_id="aa_fip_102",
                account_name="ICICI Merchant Current",
                account_type="BUSINESS",
                currency="INR",
                masked_identifier="****8765",
                provider_id=self.provider_id,
                is_selected=False,
            ),
        ]

    async def execute_action(
        self, action: str, params: Dict[str, Any], context: ExecutionContext
    ) -> Dict[str, Any]:
        if context.execution_mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
            return {
                "status": "SIMULATED",
                "provider": self.provider_id,
                "action": action,
                "detail": f"Simulated Account Aggregator '{action}'",
            }

        return {
            "status": "EXECUTED",
            "provider": self.provider_id,
            "action": action,
            "result": {"consent_id": "aa_consent_active", "data_fetched": True},
        }
