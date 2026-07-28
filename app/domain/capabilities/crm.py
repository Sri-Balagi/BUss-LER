"""Reusable Horizontal CRM Capability Module."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    loyalty_tier: str = "GOLD"
    lifetime_value_usd: float = 12000.0
    complaint_history: List[str] = Field(default_factory=list)


class CRMCapabilityModule:
    """Horizontal CRM capability engine."""

    def __init__(self):
        self._profiles: Dict[str, CustomerProfile] = {}

    def register_customer(self, profile: CustomerProfile) -> None:
        self._profiles[profile.customer_id] = profile

    def log_complaint(self, customer_id: str, complaint_text: str) -> CustomerProfile:
        if customer_id not in self._profiles:
            self._profiles[customer_id] = CustomerProfile(customer_id=customer_id, name="Valued Customer")
        self._profiles[customer_id].complaint_history.append(complaint_text)
        return self._profiles[customer_id]

    def get_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        return self._profiles.get(customer_id)
