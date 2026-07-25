"""Canonical financial objects."""
from __future__ import annotations
from datetime import datetime
from app.connectors.canonical.base import CanonicalObject


class CanonicalCustomer(CanonicalObject):
    email: str = ""
    name: str = ""
    phone: str | None = None
    currency: str = "USD"
    balance: float = 0.0


class CanonicalInvoice(CanonicalObject):
    customer_id: str = ""
    amount_due: float = 0.0
    amount_paid: float = 0.0
    currency: str = "USD"
    status: str = "draft"  # draft, open, paid, void, uncollectible
    due_date: datetime | None = None
    paid_at: datetime | None = None


class CanonicalPayment(CanonicalObject):
    amount: float = 0.0
    currency: str = "USD"
    status: str = "succeeded"  # succeeded, pending, failed
    customer_id: str | None = None
    invoice_id: str | None = None
    payment_method: str = "card"


class CanonicalOrder(CanonicalObject):
    customer_id: str = ""
    total_amount: float = 0.0
    currency: str = "USD"
    status: str = "pending"  # pending, processing, completed, cancelled
    item_count: int = 0
    fulfillment_status: str = "unfulfilled"
