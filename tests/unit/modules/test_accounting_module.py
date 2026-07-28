"""Unit tests for Financial Accounting Horizontal Business Module."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.modules.kernel.kernel_models import Contact, Customer, Money
from app.core.modules.manager import ModuleManager
from app.core.modules.models import ModuleContext
from app.core.modules.registry import ModuleRegistry
from app.modules.accounting.domain.models import (
    Account,
    AccountType,
    GeneralLedgerLine,
    Invoice,
    InvoiceLineItem,
)
from app.modules.accounting.module import AccountingModule


@pytest.mark.asyncio
async def test_accounting_module_full_lifecycle():
    module = AccountingModule()
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)
    ctx = ModuleContext(tenant_id="acct_tenant_01")

    # Install & Initialize
    assert await manager.install_module(module, ctx) is True
    assert await manager.initialize_module(module.manifest.module_id, ctx) is True
    assert await manager.enable_module(module.manifest.module_id, ctx) is True

    # Test IPaymentProvider Contract Implementation
    payment_res = await module.payment_service.process_payment(
        tenant_id="acct_tenant_01",
        amount=Money(amount=Decimal("250.00")),
        payment_method="CREDIT_CARD",
        reference_id="REF-PAY-9901"
    )
    assert payment_res["status"] == "SETTLED"
    assert payment_res["amount"] == 250.0

    refund_res = await module.payment_service.refund_payment("acct_tenant_01", payment_res["transaction_id"], Money(amount=Decimal("50.00")))
    assert refund_res is True

    # Test Invoice Generation
    customer = Customer(
        customer_id=uuid4(),
        tenant_id="acct_tenant_01",
        first_name="Jane",
        last_name="Doe",
        contact=Contact(email="jane.doe@example.com")
    )
    line1 = InvoiceLineItem(
        description="Software Consulting Services",
        quantity=10.0,
        unit_price=Money(amount=Decimal("150.00")),
        tax_rate_percent=10.0  # 10% VAT
    )
    invoice = Invoice(
        tenant_id="acct_tenant_01",
        invoice_number="INV-2026-001",
        customer=customer,
        line_items=[line1],
        due_date=datetime.utcnow()
    )
    issued_invoice = await module.invoicing_service.issue_invoice(invoice)
    assert issued_invoice.status.value == "ISSUED"
    # Subtotal $1500 + 10% tax = $1650
    assert issued_invoice.total_amount.amount == Decimal("1650.00")

    # Test General Ledger posting
    acct = Account(
        code="1010",
        name="Cash & Cash Equivalents",
        account_type=AccountType.ASSET,
        balance=Money(amount=Decimal("10000.00"))
    )
    await module.ledger_service.create_account(acct)
    gl_line = GeneralLedgerLine(
        account_id=acct.account_id,
        debit=Money(amount=Decimal("1650.00")),
        credit=Money(amount=Decimal("0.00")),
        description="Invoice payment deposit"
    )
    posted = await module.ledger_service.post_journal_entry(gl_line)
    assert posted.debit.amount == Decimal("1650.00")

    # Test Financial Analytics & DSO
    revenue = Money(amount=Decimal("100000.00"))
    receivables = Money(amount=Decimal("20000.00"))
    analytics = module.analytics_service.calculate_financial_analytics(revenue, receivables, target_dso=45.0)
    # DSO = (20000/100000) * 365 = 73 days
    assert analytics.days_sales_outstanding == 73.0
    assert "Days Sales Outstanding (73.0 days) exceeds target" in analytics.recommendation

    # Verify Declarative Business Knowledge Model (Subsystem 1)
    km = module.get_knowledge_model()
    assert km is not None
    assert len(km.vocabulary.terms) >= 2
    assert len(km.decision_frameworks) >= 1

    # Verify AI Knowledge Pack (Backward Compatibility)
    ai_pack = module.get_ai_knowledge_pack()
    assert len(ai_pack.vocabularies) >= 2


    # Verify Extension Points & Capabilities
    assert len(module.get_extension_points()) >= 1
    assert len(module.get_capabilities()) >= 2
    assert len(module.get_ui_navigation()) >= 3
