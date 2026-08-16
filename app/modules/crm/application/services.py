"""CRM Application Services implementing sales pipeline & customer management workflows."""

import logging
from decimal import Decimal
from uuid import UUID

from app.core.modules.contracts.contracts import ICustomerProvider
from app.core.modules.kernel.kernel_models import Customer, Money
from app.modules.crm.domain.events import (
    LeadCreatedEvent,
    OpportunityLostEvent,
    OpportunityWonEvent,
    PipelineStageUpdatedEvent,
)
from app.modules.crm.domain.models import (
    DealStage,
    Lead,
    SalesAnalytics,
    SalesOpportunity,
)
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class CustomerService(ICustomerProvider):
    """Customer service implementing the ICustomerProvider module contract."""

    def __init__(self) -> None:
        self._customers: dict[str, Customer] = {}

    async def get_customer(self, tenant_id: str, customer_id: UUID) -> Customer | None:
        """Retrieve customer profile by ID."""
        return self._customers.get(str(customer_id))

    async def search_customers(self, tenant_id: str, query: str, limit: int = 10) -> list[Customer]:
        """Search customers by name or email."""
        q = query.lower()
        results = []
        for cust in self._customers.values():
            if cust.tenant_id == tenant_id:
                name = f"{cust.first_name} {cust.last_name}".lower()
                email = cust.contact.email.lower() if (cust.contact and cust.contact.email) else ""
                if q in name or q in email:
                    results.append(cust)
                    if len(results) >= limit:
                        break
        return results

    async def create_customer(self, customer: Customer) -> Customer:
        """Register or update customer profile."""
        self._customers[str(customer.customer_id)] = customer
        logger.info(f"Registered CRM customer {customer.customer_id}")
        return customer


class LeadManagementService:
    """Service managing inbound lead intake and qualification."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._leads: dict[UUID, Lead] = {}
        self._event_bus = event_bus

    async def create_lead(self, lead: Lead) -> Lead:
        """Create new sales lead."""
        self._leads[lead.lead_id] = lead
        logger.info(f"Created sales lead {lead.lead_id} ({lead.first_name} {lead.last_name})")

        if self._event_bus:
            self._event_bus.publish(
                LeadCreatedEvent(
                    correlation_id=str(lead.lead_id),
                    lead_id=lead.lead_id,
                    first_name=lead.first_name,
                    last_name=lead.last_name,
                    tenant_id=lead.tenant_id
                )
            )

        return lead

    async def get_lead(self, lead_id: UUID) -> Lead | None:
        """Retrieve lead by ID."""
        return self._leads.get(lead_id)


class SalesOpportunityService:
    """Service managing sales pipeline opportunities and deal progression."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._opportunities: dict[UUID, SalesOpportunity] = {}
        self._event_bus = event_bus

    async def create_opportunity(self, opportunity: SalesOpportunity) -> SalesOpportunity:
        """Create new deal opportunity."""
        self._opportunities[opportunity.opportunity_id] = opportunity
        logger.info(f"Created opportunity {opportunity.opportunity_id} value={opportunity.deal_value.amount}")
        return opportunity

    async def update_stage(self, opportunity_id: UUID, new_stage: DealStage) -> SalesOpportunity:
        """Advance deal to new pipeline stage."""
        opp = self._opportunities.get(opportunity_id)
        if not opp:
            raise ValueError(f"Opportunity {opportunity_id} not found")

        prev_stage = opp.stage.value
        opp.stage = new_stage

        logger.info(f"Advanced opportunity {opportunity_id} from {prev_stage} to {new_stage.value}")

        if self._event_bus:
            self._event_bus.publish(
                PipelineStageUpdatedEvent(
                    correlation_id=str(opportunity_id),
                    opportunity_id=opportunity_id,
                    previous_stage=prev_stage,
                    new_stage=new_stage.value,
                    tenant_id=opp.tenant_id
                )
            )

            if new_stage == DealStage.CLOSED_WON:
                self._event_bus.publish(
                    OpportunityWonEvent(
                        correlation_id=str(opportunity_id),
                        opportunity_id=opportunity_id,
                        customer_id=opp.customer.customer_id,
                        deal_value_cents=int(opp.deal_value.amount * 100),
                        tenant_id=opp.tenant_id
                    )
                )
            elif new_stage == DealStage.CLOSED_LOST:
                self._event_bus.publish(
                    OpportunityLostEvent(
                        correlation_id=str(opportunity_id),
                        opportunity_id=opportunity_id,
                        customer_id=opp.customer.customer_id,
                        tenant_id=opp.tenant_id
                    )
                )

        return opp


class CRMAnalyticsService:
    """Service calculating pipeline totals, weighted pipeline value, and Win Rate %."""

    @staticmethod
    def calculate_sales_analytics(
        opportunities: list[SalesOpportunity],
        target_win_rate: float = 30.0
    ) -> SalesAnalytics:
        """Calculate sales pipeline analytics."""
        total_val = Money(amount=Decimal("0.00"))
        weighted_val = Money(amount=Decimal("0.00"))
        won_count = 0
        lost_count = 0
        total_count = len(opportunities)

        for opp in opportunities:
            total_val = total_val.add(opp.deal_value)
            prob = Decimal(str(opp.probability_percent / 100.0))
            weighted_val = weighted_val.add(opp.deal_value.multiply(prob))

            if opp.stage == DealStage.CLOSED_WON:
                won_count += 1
            elif opp.stage == DealStage.CLOSED_LOST:
                lost_count += 1

        closed_total = won_count + lost_count
        win_rate = (won_count / closed_total * 100.0) if closed_total > 0 else 0.0

        rec = None
        if win_rate < target_win_rate and closed_total > 0:
            rec = f"Win Rate ({win_rate:.1f}%) is below target ({target_win_rate:.1f}%). Suggest auditing proposal stage conversion rates and providing sales coaching."

        return SalesAnalytics(
            total_pipeline_value=total_val,
            weighted_pipeline_value=weighted_val,
            total_deals=total_count,
            closed_won_deals=won_count,
            closed_lost_deals=lost_count,
            win_rate_percentage=round(win_rate, 2),
            target_win_rate_percentage=target_win_rate,
            recommendation=rec
        )
