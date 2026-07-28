"""Financial Accounting Business Module implementation extending HorizontalModule."""

from app.core.modules.ai.cognition import BusinessKnowledgeModel
from app.core.modules.ai.knowledge import ModuleKnowledgePack
from app.core.modules.base import HorizontalModule
from app.core.modules.discovery.discovery import ModuleCapabilityDescriptor
from app.core.modules.extension_points.extension_points import ModuleExtensionPoint
from app.core.modules.models import ModuleContext
from app.core.modules.services.ui_metadata import UINavigationItem
from app.modules.accounting.ai.cognition import ACCOUNTING_KNOWLEDGE_MODEL
from app.modules.accounting.ai.knowledge import ACCOUNTING_KNOWLEDGE_PACK
from app.modules.accounting.application.services import (
    FinancialAnalyticsService,
    GeneralLedgerService,
    InvoicingService,
    PaymentService,
)
from app.modules.accounting.manifest import ACCOUNTING_MANIFEST


class AccountingModule(HorizontalModule):
    """Canonical Financial Accounting Business Module for BizOS Ecosystem."""

    def __init__(self) -> None:
        super().__init__(ACCOUNTING_MANIFEST)
        self.payment_service = PaymentService()
        self.invoicing_service = InvoicingService()
        self.ledger_service = GeneralLedgerService()
        self.analytics_service = FinancialAnalyticsService()

    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize accounting services, platform capabilities, extension points, and UI metadata."""
        await super().initialize(context)
        return True

    def get_knowledge_model(self) -> BusinessKnowledgeModel:
        """Expose Subsystem 1 BusinessKnowledgeModel declaration."""
        return ACCOUNTING_KNOWLEDGE_MODEL

    def get_ai_knowledge_pack(self) -> ModuleKnowledgePack:
        """Expose legacy AI knowledge pack for backward compatibility."""
        return ACCOUNTING_KNOWLEDGE_PACK


    def get_extension_points(self) -> list[ModuleExtensionPoint]:
        """Expose extension points for third-party modules to extend accounting functionality."""
        return [
            ModuleExtensionPoint(
                point_id="bizos.modules.accounting.invoice_tax_calculation_hook",
                module_id=self.manifest.module_id,
                name="Invoice Tax Calculation Interceptor Hook",
                description="Allows regional tax engines to calculate multi-jurisdiction VAT/GST on invoices."
            )
        ]

    def get_capabilities(self) -> list[ModuleCapabilityDescriptor]:
        """Expose runtime capability descriptors for AI agents."""
        return [
            ModuleCapabilityDescriptor(
                capability_id="accounting_payment_processing",
                module_id=self.manifest.module_id,
                name="Payment & Transaction Settlement",
                description="Processes customer payments and handles refunds.",
                category="finance"
            ),
            ModuleCapabilityDescriptor(
                capability_id="accounting_financial_analytics",
                module_id=self.manifest.module_id,
                name="Cash Flow & DSO Analytics",
                description="Calculates Days Sales Outstanding (DSO) and cash flow ratios.",
                category="analytics"
            )
        ]

    def get_ui_navigation(self) -> list[UINavigationItem]:
        """Expose declarative UI navigation menu items."""
        return [
            UINavigationItem(item_id="acct_invoices", label="Customer Invoices", icon="file-text", route="/accounting/invoices", order=1),
            UINavigationItem(item_id="acct_ledger", label="General Ledger", icon="book-open", route="/accounting/ledger", order=2),
            UINavigationItem(item_id="acct_analytics", label="Financial Analytics", icon="pie-chart", route="/accounting/analytics", order=3)
        ]
