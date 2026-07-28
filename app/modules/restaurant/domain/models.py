"""Restaurant Domain entities and value objects leveraging Shared Domain Kernel models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.kernel.kernel_models import Customer, Money


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReservationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    SEATED = "SEATED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"


class Ingredient(BaseModel):
    """Ingredient entity for recipes and inventory tracking."""

    ingredient_id: UUID = Field(default_factory=uuid4)
    name: str
    unit_of_measure: str  # grams, oz, liters
    current_stock: float
    reorder_threshold: float
    cost_per_unit: Money


class Recipe(BaseModel):
    """Recipe mapping ingredients to menu items."""

    recipe_id: UUID = Field(default_factory=uuid4)
    name: str
    ingredients: list[dict[str, Any]] = Field(default_factory=list)  # [{"ingredient_id": "...", "qty": 150}]

    def calculate_raw_cost(self, ingredient_costs: dict[str, Money]) -> Money:
        """Calculate total raw ingredient cost for recipe."""
        total = Money(amount=Decimal("0.00"))
        for item in self.ingredients:
            ing_id = str(item.get("ingredient_id"))
            qty = Decimal(str(item.get("qty", 1.0)))
            if ing_id in ingredient_costs:
                unit_cost = ingredient_costs[ing_id]
                item_cost = unit_cost.multiply(qty)
                total = total.add(item_cost)
        return total


class MenuItem(BaseModel):
    """Menu Item offered by the restaurant."""

    item_id: UUID = Field(default_factory=uuid4)
    name: str
    category: str  # Appetizer, Main, Dessert, Beverage
    price: Money
    recipe: Recipe | None = None
    is_available: bool = True


class OrderItem(BaseModel):
    """Item line within a customer order."""

    item_id: UUID
    item_name: str
    quantity: int = 1
    unit_price: Money
    special_instructions: str | None = None

    @property
    def total_price(self) -> Money:
        return self.unit_price.multiply(self.quantity)


class Order(BaseModel):
    """Order aggregate root."""

    order_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    table_number: int | None = None
    customer: Customer | None = None
    items: list[OrderItem] = Field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_amount(self) -> Money:
        total = Money(amount=Decimal("0.00"))
        for item in self.items:
            total = total.add(item.total_price)
        return total


class Table(BaseModel):
    """Table entity in restaurant dining room."""

    table_id: UUID = Field(default_factory=uuid4)
    table_number: int
    capacity: int = 4
    is_occupied: bool = False
    assigned_waiter: str | None = None


class Reservation(BaseModel):
    """Customer reservation entity."""

    reservation_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    customer_name: str
    customer_phone: str
    party_size: int
    reservation_time: datetime
    status: ReservationStatus = ReservationStatus.CONFIRMED


class KitchenTicket(BaseModel):
    """Kitchen Display System ticket."""

    ticket_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    table_number: int | None = None
    items_summary: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "QUEUED"  # QUEUED, COOKING, READY
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Supplier(BaseModel):
    """Food & Beverage Supplier entity."""

    supplier_id: UUID = Field(default_factory=uuid4)
    name: str
    contact_email: str
    supplied_ingredients: list[str] = Field(default_factory=list)


class FoodCostAnalytics(BaseModel):
    """Analytics metric container for Food Cost calculation."""

    total_revenue: Money
    total_cost_of_goods: Money
    food_cost_percentage: float
    target_food_cost_percentage: float = 30.0
    recommendation: str | None = None
