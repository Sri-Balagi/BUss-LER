"""Financial Accounting Domain entities and value objects leveraging Shared Domain Kernel models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.kernel.kernel_models import (
    Customer,
    Money,
    Organization,
    TaxInfo,
)


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    CASH = "CASH"
    CHECK = "CHECK"
    CRYPTO = "CRYPTO"


class Account(BaseModel):
    """General Ledger Account entity in Chart of Accounts."""

    account_id: UUID = Field(default_factory=uuid4)
    code: str  # e.g. "1010"
    name: str  # e.g. "Cash & Cash Equivalents"
    account_type: AccountType
    balance: Money
    is_active: bool = True


class GeneralLedgerLine(BaseModel):
    """Journal entry line item."""

    line_id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    debit: Money
    credit: Money
    description: str | None = None


class InvoiceLineItem(BaseModel):
    """Line item in a customer/vendor invoice."""

    item_id: UUID = Field(default_factory=uuid4)
    description: str
    quantity: float = 1.0
    unit_price: Money
    tax_rate_percent: float = 0.0

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(Decimal(str(self.quantity)))

    @property
    def total(self) -> Money:
        tax_mult = Decimal("1.0") + (Decimal(str(self.tax_rate_percent)) / Decimal("100.0"))
        return self.subtotal.multiply(tax_mult)


class Invoice(BaseModel):
    """Customer Invoice aggregate root."""

    invoice_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    invoice_number: str
    customer: Customer  # Reuses Shared Domain Kernel Customer model
    organization: Organization | None = None
    line_items: list[InvoiceLineItem] = Field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    tax_info: TaxInfo | None = None

    @property
    def total_amount(self) -> Money:
        total = Money(amount=Decimal("0.00"))
        for item in self.line_items:
            total = total.add(item.total)
        return total


class PaymentReceipt(BaseModel):
    """Payment transaction receipt."""

    receipt_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    invoice_id: UUID
    amount_paid: Money
    payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD
    payment_reference: str
    received_at: datetime = Field(default_factory=datetime.utcnow)


class FiscalPeriod(BaseModel):
    """Fiscal accounting period."""

    period_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    period_name: str  # e.g. "Q1-2026"
    start_date: datetime
    end_date: datetime
    is_closed: bool = False


class FinancialAnalytics(BaseModel):
    """Container for Financial & Cash Flow Analytics metrics."""

    total_revenue: Money
    total_receivables: Money
    days_sales_outstanding: float
    target_dso_days: float = 45.0
    quick_ratio: float
    gross_margin_percent: float
    recommendation: str | None = None
