"""Pinnacle Global Wealth — Reference Business Plugin for Financial Services & Banking."""

from typing import Any, Dict, List
from app.infrastructure.plugins.base import IBusinessPlugin


class FinancePlugin(IBusinessPlugin):
    """Reference Business Plugin for Banking, Risk & Compliance Operations."""

    @property
    def plugin_name(self) -> str:
        return "finance"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def initialize(self) -> None:
        pass

    def get_knowledge_documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Anti-Money Laundering (AML) Compliance Rule #801",
                "source": "compliance_manual_v4",
                "content": (
                    "AML COMPLIANCE RULE #801: Automated Freeze & Escalation.\n"
                    "1. Transactions exceeding $50,000 USD originating from high-risk IP locations must trigger an immediate account hold.\n"
                    "2. Require mandatory human compliance officer review (Human-in-the-Loop Checkpoint).\n"
                    "3. Perform automatic vault liquidity rebalancing if interbank cash reserves drop below $2,000,000 USD."
                ),
            },
            {
                "title": "Vault Liquidity & Capital Reserves SOP #403",
                "source": "treasury_sop",
                "content": (
                    "TREASURY SOP #403:\n"
                    "Maintain minimum tier-1 capital reserve ratio of 12.5%. Execute intra-day repo transfer if liquidity drops below threshold."
                ),
            },
        ]

    def get_initial_digital_twin_properties(self) -> Dict[str, Any]:
        return {
            "institution_name": "Pinnacle Global Wealth",
            "vault_cash_reserve_usd": 1850000.0,
            "flagged_aml_accounts": 3,
            "transaction_velocity_sec": 420,
            "capital_reserve_ratio": "11.8% (Target: >= 12.5%)",
            "compliance_hold_active": True,
        }

    def get_crisis_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "FIN-001",
                "title": "High-Frequency AML Wire Fraud Alert & Reserve Shortage",
                "objective": "CRISIS: Flagged $75k wire transfer from suspicious IP. Vault cash reserve at $1.85M (below $2M threshold). Trigger account freeze, Human Compliance Checkpoint, and liquidity rebalance.",
                "priority": "CRITICAL",
                "agent_name": "FinanceRiskAgent",
            }
        ]
