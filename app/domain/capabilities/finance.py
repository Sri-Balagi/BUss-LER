"""Reusable Horizontal Finance & Ledger Capability Module."""

from typing import Any, Dict, List
from uuid import uuid4
from pydantic import BaseModel, Field


class TransactionRecord(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid4()))
    account_id: str
    amount_usd: float
    type: str  # CREDIT, DEBIT, REFUND
    risk_score: float = 0.1
    status: str = "COMPLETED"


class FinanceCapabilityModule:
    """Horizontal Finance capability engine."""

    def __init__(self):
        self._transactions: List[TransactionRecord] = []

    def issue_refund(self, account_id: str, amount_usd: float, reason: str = "") -> TransactionRecord:
        tx = TransactionRecord(
            account_id=account_id,
            amount_usd=amount_usd,
            type="REFUND",
            status="COMPLETED",
        )
        self._transactions.append(tx)
        return tx

    def evaluate_transaction_risk(self, account_id: str, amount_usd: float) -> TransactionRecord:
        risk_score = 0.92 if amount_usd > 50000.0 else 0.12
        tx = TransactionRecord(
            account_id=account_id,
            amount_usd=amount_usd,
            type="DEBIT",
            risk_score=risk_score,
            status="FLAGGED" if risk_score > 0.85 else "COMPLETED",
        )
        self._transactions.append(tx)
        return tx
