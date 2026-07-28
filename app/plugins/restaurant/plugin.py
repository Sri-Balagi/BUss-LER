"""Bella Vista Restaurant Group — Reference Business Plugin for BizOS."""

from typing import Any, Dict, List
from app.infrastructure.plugins.base import IBusinessPlugin


class RestaurantPlugin(IBusinessPlugin):
    """Reference implementation of a domain business plugin for Restaurant Operations."""

    @property
    def plugin_name(self) -> str:
        return "restaurant"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def initialize(self) -> None:
        pass

    def get_knowledge_documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Kitchen Staff Shortage Emergency Protocol",
                "source": "sop_manual_v3",
                "content": (
                    "OPERATIONAL SOP #402: Kitchen Staff Shortage Protocol.\n"
                    "1. When Head Chef is absent or kitchen is understaffed by 2+ cooks, immediately promote Sous Chef (Sofia) to Lead Kitchen Command.\n"
                    "2. Request 2 emergency backup prep cooks from Branch #1 (ETA SLA: <= 25 minutes).\n"
                    "3. Simplify active dining menu to 12 core high-throughput dishes to reduce ticket prep time from 18 min to 8 min.\n"
                    "4. Reprioritize order dispatch queue by customer wait duration (oldest ticket first)."
                ),
            },
            {
                "title": "VIP Corporate Guest Experience Protocol (Apex Corp Account)",
                "source": "vip_services_guide",
                "content": (
                    "VIP SERVICE GUIDELINE #109: Apex Corp Annual Account ($120k/yr).\n"
                    "1. Reserved Seating: Lock Tables 15-22 exclusively in main dining hall.\n"
                    "2. Host Assignment: Assign Senior Server Carlos (5yr seniority).\n"
                    "3. Hospitality Package: Deploy complimentary prosecco welcome & 4-course preset menu immediately upon seating.\n"
                    "4. SLA Guarantee: Zero wait time upon arrival."
                ),
            },
            {
                "title": "Service Recovery & Customer Wait SLA Policy",
                "source": "customer_experience_manual",
                "content": (
                    "SERVICE RECOVERY POLICY #204: Wait SLA target is <= 20 minutes.\n"
                    "1. If average wait time exceeds 35 minutes, trigger automated SMS blast with 15% discount code to waiting guests.\n"
                    "2. Deploy complimentary bread and olive oil basket to all occupied tables immediately.\n"
                    "3. Post manager check-ins to tables reporting negative review sentiment."
                ),
            },
            {
                "title": "Downtown Branch Operating Profile & Specs",
                "source": "branch_specs",
                "content": (
                    "BELLA VISTA DOWNTOWN BRANCH SPECIFICATIONS:\n"
                    "Address: 42 West 5th Street.\n"
                    "Total Table Capacity: 40 tables (160 seats).\n"
                    "Current Occupancy: 34/40 tables occupied.\n"
                    "Head Chef: Marco Rossi.\n"
                    "Sous Chef: Sofia (Certified head cook, 3 yrs experience).\n"
                    "Dedicated Senior Hosts: Carlos, Maria."
                ),
            },
        ]

    def get_initial_digital_twin_properties(self) -> Dict[str, Any]:
        return {
            "branch_name": "Bella Vista Downtown",
            "table_capacity": 40,
            "occupied_tables": 34,
            "wait_time_minutes": 47,
            "wait_time_sla_minutes": 20,
            "kitchen_backlog_orders": 23,
            "head_chef_status": "Marco Rossi - Called in Sick",
            "active_lead_chef": "Sofia - Promoted Sous Chef",
            "staffing_shortage_count": 2,
            "vip_guest": "Apex Corp (18 guests at 20:00)",
            "vip_reserved_tables": "Tables 15-22",
            "vip_server": "Carlos",
            "kpi_satisfaction": "2.1 stars (Target: 4.3+)",
        }

    def get_crisis_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "G-001",
                "title": "Kitchen Staffing Emergency",
                "objective": (
                    "CRISIS: Head chef Marco Rossi called in sick. Kitchen is understaffed by 2 people. "
                    "Promote sous chef Sofia to lead kitchen for tonight. Contact Branch #1 to send 2 backup staff. "
                    "Ensure all 23 queued orders are processed within 30 minutes."
                ),
                "priority": "CRITICAL",
                "agent_name": "OpsCommandAgent",
            },
            {
                "id": "G-002",
                "title": "VIP Guest Experience -- Apex Corp",
                "objective": (
                    "VIP PRIORITY: Corporate party of 18 guests (Apex Corp, annual $120k account) arriving at 20:00. "
                    "Reserve tables 15-22 exclusively. Assign senior server Carlos. "
                    "Prepare complimentary welcome prosecco and 4-course pre-set menu. Ensure zero wait on arrival."
                ),
                "priority": "HIGH",
                "agent_name": "GuestExperienceAgent",
            },
            {
                "id": "G-003",
                "title": "Service Recovery -- Wait Time Crisis",
                "objective": (
                    "SERVICE FAILURE: Average wait time is 47 minutes against 20-minute SLA. "
                    "6 negative reviews posted in 2 hours averaging 2.1 stars. "
                    "Simplify active menu to 12 core items. Send 15% discount SMS to all waiting guests. "
                    "Deploy complimentary bread service immediately to all occupied tables."
                ),
                "priority": "HIGH",
                "agent_name": "ServiceRecoveryAgent",
            },
        ]
