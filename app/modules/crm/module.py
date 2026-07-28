"""CRM & Sales Pipeline Business Module implementation extending HorizontalModule."""

from app.core.modules.ai.cognition import BusinessKnowledgeModel
from app.core.modules.ai.knowledge import ModuleKnowledgePack
from app.core.modules.base import HorizontalModule
from app.core.modules.discovery.discovery import ModuleCapabilityDescriptor
from app.core.modules.extension_points.extension_points import ModuleExtensionPoint
from app.core.modules.models import ModuleContext
from app.core.modules.services.ui_metadata import UINavigationItem
from app.modules.crm.ai.cognition import CRM_KNOWLEDGE_MODEL
from app.modules.crm.ai.knowledge import CRM_KNOWLEDGE_PACK
from app.modules.crm.application.services import (
    CRMAnalyticsService,
    CustomerService,
    LeadManagementService,
    SalesOpportunityService,
)
from app.modules.crm.manifest import CRM_MANIFEST


class CRMModule(HorizontalModule):
    """Canonical CRM & Sales Pipeline Business Module for BizOS Ecosystem."""

    def __init__(self) -> None:
        super().__init__(CRM_MANIFEST)
        self.customer_service = CustomerService()
        self.lead_service = LeadManagementService()
        self.opportunity_service = SalesOpportunityService()
        self.analytics_service = CRMAnalyticsService()

    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize CRM services, platform capabilities, extension points, and UI metadata."""
        await super().initialize(context)
        return True

    def get_knowledge_model(self) -> BusinessKnowledgeModel:
        """Expose Subsystem 1 BusinessKnowledgeModel declaration."""
        return CRM_KNOWLEDGE_MODEL

    def get_ai_knowledge_pack(self) -> ModuleKnowledgePack:
        """Expose legacy AI knowledge pack for backward compatibility."""
        return CRM_KNOWLEDGE_PACK


    def get_extension_points(self) -> list[ModuleExtensionPoint]:
        """Expose extension points for third-party modules to extend CRM functionality."""
        return [
            ModuleExtensionPoint(
                point_id="bizos.modules.crm.deal_stage_change_hook",
                module_id=self.manifest.module_id,
                name="Deal Stage Change Interceptor Hook",
                description="Allows automation, commission, or analytics modules to hook into deal stage transitions."
            )
        ]

    def get_capabilities(self) -> list[ModuleCapabilityDescriptor]:
        """Expose runtime capability descriptors for AI agents."""
        return [
            ModuleCapabilityDescriptor(
                capability_id="crm_customer_management",
                module_id=self.manifest.module_id,
                name="Customer Profile Management",
                description="Registers, retrieves, and manages enterprise customer profiles.",
                category="crm"
            ),
            ModuleCapabilityDescriptor(
                capability_id="crm_pipeline_analytics",
                module_id=self.manifest.module_id,
                name="Sales Pipeline & Win Rate Analytics",
                description="Calculates total pipeline value, weighted deal values, and win rates.",
                category="analytics"
            )
        ]

    def get_ui_navigation(self) -> list[UINavigationItem]:
        """Expose declarative UI navigation menu items."""
        return [
            UINavigationItem(item_id="crm_leads", label="Sales Leads", icon="user-plus", route="/crm/leads", order=1),
            UINavigationItem(item_id="crm_deals", label="Sales Pipeline Deals", icon="dollar-sign", route="/crm/deals", order=2),
            UINavigationItem(item_id="crm_analytics", label="Sales Win Rate Analytics", icon="trending-up", route="/crm/analytics", order=3)
        ]
