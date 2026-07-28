"""Unit tests for CRM & Sales Pipeline Horizontal Business Module."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.modules.kernel.kernel_models import Contact, Customer, Money
from app.core.modules.manager import ModuleManager
from app.core.modules.models import ModuleContext
from app.core.modules.registry import ModuleRegistry
from app.modules.crm.domain.models import DealStage, Lead, SalesOpportunity
from app.modules.crm.module import CRMModule


@pytest.mark.asyncio
async def test_crm_module_full_lifecycle():
    module = CRMModule()
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)
    ctx = ModuleContext(tenant_id="crm_tenant_01")

    # Install & Initialize
    assert await manager.install_module(module, ctx) is True
    assert await manager.initialize_module(module.manifest.module_id, ctx) is True
    assert await manager.enable_module(module.manifest.module_id, ctx) is True

    # Test ICustomerProvider Contract Implementation
    cust_id = uuid4()
    customer = Customer(
        customer_id=cust_id,
        tenant_id="crm_tenant_01",
        first_name="Alice",
        last_name="Smith",
        contact=Contact(email="alice.smith@acme.com")
    )
    created_cust = await module.customer_service.create_customer(customer)
    assert created_cust.first_name == "Alice"

    retrieved = await module.customer_service.get_customer("crm_tenant_01", cust_id)
    assert retrieved is not None
    assert retrieved.last_name == "Smith"

    search_res = await module.customer_service.search_customers("crm_tenant_01", "acme.com")
    assert len(search_res) == 1

    # Test Lead Creation
    lead = Lead(
        tenant_id="crm_tenant_01",
        first_name="Bob",
        last_name="Jones",
        company_name="TechCorp",
        email="bob.jones@techcorp.io"
    )
    created_lead = await module.lead_service.create_lead(lead)
    assert created_lead.company_name == "TechCorp"

    # Test Sales Opportunity & Pipeline Stage Advancement
    opp = SalesOpportunity(
        tenant_id="crm_tenant_01",
        title="Enterprise CRM Contract",
        customer=customer,
        deal_value=Money(amount=Decimal("50000.00")),
        stage=DealStage.PROSPECTING,
        probability_percent=20.0
    )
    created_opp = await module.opportunity_service.create_opportunity(opp)
    assert created_opp.deal_value.amount == Decimal("50000.00")

    # Advance deal stage to CLOSED_WON
    updated_opp = await module.opportunity_service.update_stage(opp.opportunity_id, DealStage.CLOSED_WON)
    assert updated_opp.stage == DealStage.CLOSED_WON

    # Test CRM Sales Analytics
    analytics = module.analytics_service.calculate_sales_analytics([updated_opp], target_win_rate=30.0)
    assert analytics.total_pipeline_value.amount == Decimal("50000.00")
    assert analytics.win_rate_percentage == 100.0

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
