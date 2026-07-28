"""Manifest definition for Financial Accounting Horizontal Business Module."""

from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleManifest,
    ModuleType,
)

ACCOUNTING_MANIFEST = ModuleManifest(
    module_id="bizos.modules.accounting.v1",
    name="Financial Accounting & Invoicing",
    description="Cross-industry Enterprise Financial Accounting Module for BizOS supporting General Ledger, Invoicing, Payment Receipts, Chart of Accounts, Fiscal Periods, and AI Cash Flow optimization.",
    version="1.0.0",
    module_type=ModuleType.HORIZONTAL,
    category=ModuleCategory.ACCOUNTING,
    author="BizOS Core Engineering Team",
    dependencies=[],
    required_connectors=["banking_api", "payment_gateway", "tax_engine"],
    supported_languages=["en", "es", "fr"],
    supported_regions=["US", "EU", "GLOBAL"],
    capabilities=ModuleCapabilities(
        domain_entities=["ChartOfAccounts", "GeneralLedgerLine", "Invoice", "PaymentReceipt", "FiscalPeriod"],
        commands=["IssueInvoice", "ProcessPayment", "PostJournalEntry", "CloseFiscalPeriod"],
        queries=["GetGeneralLedger", "GetInvoiceStatus", "GetFinancialAnalytics"],
        events_published=["InvoiceGenerated", "PaymentReceived", "FiscalPeriodClosed"],
        events_subscribed=["OrderPlaced", "OrderCompleted", "OpportunityWon"],
        permissions=["accounting:ledger:manage", "accounting:invoice:create", "accounting:reports:view"],
        ai_vocabularies=["Days Sales Outstanding", "Quick Ratio", "Gross Margin Percentage"],
        provided_contracts=["IPaymentProvider"]
    ),
    marketplace=MarketplaceMetadata(
        publisher="BizOS Official",
        website="https://bizos.ai/modules/accounting",
        support_email="accounting-support@bizos.ai",
        license="Enterprise-Proprietary",
        min_bizos_version="1.0.0",
        price_model="subscription",
        tags=["accounting", "finance", "invoicing", "payments", "ledger", "tax"]
    ),
    configuration_schema={
        "fiscal_year_start_month": {"type": "integer", "default": 1},
        "default_payment_terms_days": {"type": "integer", "default": 30},
        "target_dso_days": {"type": "number", "default": 45.0}
    }
)
