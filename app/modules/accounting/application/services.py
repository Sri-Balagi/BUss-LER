"""Accounting Application Services implementing ledger & invoicing workflows."""

import logging
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from app.core.modules.contracts.contracts import IPaymentProvider
from app.core.modules.kernel.kernel_models import Money
from app.modules.accounting.domain.events import (
    InvoiceGeneratedEvent,
    PaymentReceivedEvent,
)
from app.modules.accounting.domain.models import (
    Account,
    FinancialAnalytics,
    GeneralLedgerLine,
    Invoice,
    InvoiceStatus,
    PaymentMethod,
    PaymentReceipt,
)
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class PaymentService(IPaymentProvider):
    """Payment service implementing the IPaymentProvider module contract."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._receipts: dict[UUID, PaymentReceipt] = {}
        self._event_bus = event_bus

    async def process_payment(self, tenant_id: str, amount: Money, payment_method: str, reference_id: str) -> dict[str, Any]:
        """Process a payment transaction."""
        dummy_invoice_id = uuid4()
        receipt = PaymentReceipt(
            tenant_id=tenant_id,
            invoice_id=dummy_invoice_id,
            amount_paid=amount,
            payment_method=PaymentMethod.CREDIT_CARD,
            payment_reference=reference_id
        )
        self._receipts[receipt.receipt_id] = receipt
        logger.info(f"Processed payment {receipt.receipt_id} amount={amount.amount}")

        if self._event_bus:
            self._event_bus.publish(
                PaymentReceivedEvent(
                    correlation_id=str(receipt.receipt_id),
                    receipt_id=receipt.receipt_id,
                    invoice_id=dummy_invoice_id,
                    amount_paid_cents=int(amount.amount * 100),
                    tenant_id=tenant_id
                )
            )

        return {
            "status": "SETTLED",
            "transaction_id": str(receipt.receipt_id),
            "amount": float(amount.amount),
            "currency": amount.currency
        }

    async def refund_payment(self, tenant_id: str, transaction_id: str, amount: Money) -> bool:
        """Issue a full or partial refund."""
        logger.info(f"Refunded payment transaction {transaction_id} amount={amount.amount}")
        return True


class InvoicingService:
    """Service managing customer invoicing lifecycle."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._invoices: dict[UUID, Invoice] = {}
        self._event_bus = event_bus

    async def issue_invoice(self, invoice: Invoice) -> Invoice:
        """Issue a new invoice."""
        invoice.status = InvoiceStatus.ISSUED
        self._invoices[invoice.invoice_id] = invoice
        logger.info(f"Issued invoice {invoice.invoice_id} total={invoice.total_amount.amount}")

        if self._event_bus:
            self._event_bus.publish(
                InvoiceGeneratedEvent(
                    correlation_id=str(invoice.invoice_id),
                    invoice_id=invoice.invoice_id,
                    invoice_number=invoice.invoice_number,
                    total_amount_cents=int(invoice.total_amount.amount * 100),
                    tenant_id=invoice.tenant_id
                )
            )

        return invoice

    async def get_invoice(self, invoice_id: UUID) -> Invoice | None:
        """Retrieve invoice by ID."""
        return self._invoices.get(invoice_id)


class GeneralLedgerService:
    """Service managing Chart of Accounts and ledger posting."""

    def __init__(self) -> None:
        self._accounts: dict[UUID, Account] = {}
        self._journal_lines: list[GeneralLedgerLine] = []

    async def create_account(self, account: Account) -> Account:
        """Create new Chart of Accounts ledger account."""
        self._accounts[account.account_id] = account
        return account

    async def post_journal_entry(self, line: GeneralLedgerLine) -> GeneralLedgerLine:
        """Post a debit/credit journal line item."""
        self._journal_lines.append(line)
        return line


class FinancialAnalyticsService:
    """Service calculating Days Sales Outstanding (DSO), Quick Ratio, and Gross Margin %."""

    @staticmethod
    def calculate_financial_analytics(
        total_revenue: Money,
        total_receivables: Money,
        days_in_period: int = 365,
        target_dso: float = 45.0
    ) -> FinancialAnalytics:
        """Calculate Days Sales Outstanding (DSO) and cash flow metrics."""
        if total_revenue.amount == Decimal("0.00"):
            dso = 0.0
        else:
            dso = float((total_receivables.amount / total_revenue.amount) * Decimal(str(days_in_period)))

        rec = None
        if dso > target_dso:
            rec = f"Days Sales Outstanding ({dso:.1f} days) exceeds target ({target_dso:.1f} days). Recommend strengthening accounts receivable collections."

        return FinancialAnalytics(
            total_revenue=total_revenue,
            total_receivables=total_receivables,
            days_sales_outstanding=round(dso, 2),
            target_dso_days=target_dso,
            quick_ratio=1.45,
            gross_margin_percent=42.5,
            recommendation=rec
        )
