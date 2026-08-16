"""Shared Domain Kernel models universally reusable across all BizOS modules."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"


class Money(BaseModel):
    """Immutable Value Object for monetary amounts."""

    amount: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    currency: Currency = Currency.USD

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: Decimal | int | float) -> "Money":
        return Money(amount=(self.amount * Decimal(str(factor))).quantize(Decimal("0.01")), currency=self.currency)


class Address(BaseModel):
    """Universal Address Value Object."""

    street_1: str = ""
    street_2: str | None = None
    city: str = ""
    state_province: str = ""
    postal_code: str = ""
    country: str = "US"


class Contact(BaseModel):
    """Universal Contact Information Value Object."""

    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    website: str | None = None


class TaxInfo(BaseModel):
    """Universal Tax Registration Value Object."""

    tax_id: str | None = None
    tax_jurisdiction: str | None = None
    is_tax_exempt: bool = False


class AuditContext(BaseModel):
    """Universal Audit Metadata context for tracking mutations."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str | None = None
    tenant_id: str | None = None


class EntityReference(BaseModel):
    """Universal cross-module entity reference."""

    module_id: str
    entity_type: str
    entity_id: UUID
    display_name: str | None = None


class Customer(BaseModel):
    """Shared Domain Entity representing a Business Customer."""

    customer_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    first_name: str
    last_name: str
    company_name: str | None = None
    contact: Contact = Field(default_factory=Contact)
    address: Address | None = None
    tax_info: TaxInfo | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    audit: AuditContext = Field(default_factory=AuditContext)


class Organization(BaseModel):
    """Shared Domain Entity representing an Enterprise Organization."""

    org_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    name: str
    tax_info: TaxInfo = Field(default_factory=TaxInfo)
    address: Address = Field(default_factory=Address)
    contact: Contact = Field(default_factory=Contact)
    settings: dict[str, Any] = Field(default_factory=dict)
    audit: AuditContext = Field(default_factory=AuditContext)
