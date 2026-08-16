"""Cross-Module Workflow & Human-in-the-Loop Checkpoint Orchestrator."""

import asyncio
from typing import Any, Dict, List
from uuid import UUID, uuid4

from app.domain.capabilities.crm import CRMCapabilityModule
from app.domain.capabilities.finance import FinanceCapabilityModule
from app.domain.capabilities.inventory import InventoryCapabilityModule
from app.domain.capabilities.compliance import ComplianceCapabilityModule
from app.domain.capabilities.operations import OperationsCapabilityModule


class CrossModuleWorkflowOrchestrator:
    """Orchestrates workflows spanning multiple horizontal business capabilities."""

    def __init__(self):
        self.crm = CRMCapabilityModule()
        self.finance = FinanceCapabilityModule()
        self.inventory = InventoryCapabilityModule()
        self.compliance = ComplianceCapabilityModule()
        self.operations = OperationsCapabilityModule()

    async def execute_customer_complaint_workflow(self, customer_id: str, complaint_text: str, refund_usd: float) -> Dict[str, Any]:
        """Cross-Module Workflow: CRM -> Finance -> Compliance -> Operations."""
        workflow_id = str(uuid4())
        
        # 1. CRM
        profile = self.crm.log_complaint(customer_id, complaint_text)

        # 2. Compliance Human Checkpoint
        alert = self.compliance.flag_violation(
            rule_name="Customer Refund SLA Rule #204",
            details=f"High priority complaint: {complaint_text}",
            severity="HIGH",
        )

        # Simulate Human-in-the-Loop Checkpoint
        checkpoint_status = "BLOCKED_ON_APPROVAL"
        self.compliance.approve_alert(alert.alert_id)
        checkpoint_status = "RESUMED_UPON_HUMAN_APPROVAL"

        # 3. Finance
        tx = self.finance.issue_refund(customer_id, refund_usd, reason=complaint_text)

        # 4. Operations
        res = self.operations.promote_or_assign("STAFF-01", new_role="Guest Relations Specialist")

        return {
            "workflow_id": workflow_id,
            "status": "COMPLETED",
            "checkpoint_history": [
                {"checkpoint": "Compliance Review", "status": checkpoint_status, "alert_id": alert.alert_id}
            ],
            "crm_profile": profile.model_dump(),
            "finance_refund_tx": tx.model_dump(),
            "assigned_staff": res.model_dump(),
        }
