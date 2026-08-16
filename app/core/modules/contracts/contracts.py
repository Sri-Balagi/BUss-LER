"""Standardized contracts for decoupled inter-module communication."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.core.modules.kernel.kernel_models import Customer, Money


class ICustomerProvider(ABC):
    """Public contract for retrieving and managing customer records across modules."""

    @abstractmethod
    async def get_customer(self, tenant_id: str, customer_id: UUID) -> Customer | None:
        """Fetch customer profile by ID."""
        pass

    @abstractmethod
    async def search_customers(self, tenant_id: str, query: str, limit: int = 10) -> list[Customer]:
        """Search customers by name or contact info."""
        pass


class IInventoryProvider(ABC):
    """Public contract for managing inventory levels and reservations across modules."""

    @abstractmethod
    async def check_availability(self, tenant_id: str, item_id: str, required_qty: float) -> bool:
        """Check if an inventory item has sufficient stock."""
        pass

    @abstractmethod
    async def reserve_stock(self, tenant_id: str, item_id: str, qty: float, reference_id: str) -> bool:
        """Reserve inventory quantity for an order or job."""
        pass

    @abstractmethod
    async def deduct_stock(self, tenant_id: str, item_id: str, qty: float, reference_id: str) -> bool:
        """Deduct inventory stock permanently."""
        pass


class IPaymentProvider(ABC):
    """Public contract for processing payments and transactions across modules."""

    @abstractmethod
    async def process_payment(self, tenant_id: str, amount: Money, payment_method: str, reference_id: str) -> dict[str, Any]:
        """Process a payment transaction."""
        pass

    @abstractmethod
    async def refund_payment(self, tenant_id: str, transaction_id: str, amount: Money) -> bool:
        """Issue a full or partial refund."""
        pass


class IWorkflowProvider(ABC):
    """Public contract for starting and tracking cross-module workflows."""

    @abstractmethod
    async def trigger_workflow(self, tenant_id: str, workflow_name: str, payload: dict[str, Any]) -> str:
        """Trigger an automated workflow execution."""
        pass


class INotificationProvider(ABC):
    """Public contract for sending notifications across modules."""

    @abstractmethod
    async def send_notification(self, tenant_id: str, recipient: str, template_id: str, variables: dict[str, Any]) -> bool:
        """Send an event-triggered notification."""
        pass
