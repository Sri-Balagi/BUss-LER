"""Restaurant Application Services implementing business workflows."""

import logging
from decimal import Decimal
from uuid import UUID

from app.core.modules.kernel.kernel_models import Money
from app.modules.restaurant.domain.events import (
    IngredientLowEvent,
    OrderCompletedEvent,
    OrderPlacedEvent,
)
from app.modules.restaurant.domain.models import (
    FoodCostAnalytics,
    Ingredient,
    KitchenTicket,
    Order,
    OrderItem,
    OrderStatus,
    Reservation,
)
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class OrderManagementService:
    """Service managing restaurant order lifecycle and billing."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._orders: dict[UUID, Order] = {}
        self._event_bus = event_bus

    async def create_order(self, tenant_id: str, table_number: int | None, items: list[OrderItem]) -> Order:
        """Create and place a new restaurant order."""
        order = Order(
            tenant_id=tenant_id,
            table_number=table_number,
            items=items,
            status=OrderStatus.PENDING
        )
        self._orders[order.order_id] = order
        logger.info(f"Placed restaurant order {order.order_id} total={order.total_amount.amount}")

        if self._event_bus:
            self._event_bus.publish(
                OrderPlacedEvent(
                    correlation_id=str(order.order_id),
                    order_id=order.order_id,
                    tenant_id=tenant_id,
                    table_number=table_number,
                    total_amount_cents=int(order.total_amount.amount * 100)
                )
            )

        return order

    async def get_order(self, order_id: UUID) -> Order | None:
        """Retrieve order by ID."""
        return self._orders.get(order_id)

    async def complete_order(self, order_id: UUID) -> Order:
        """Mark an order as completed and settled."""
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.status = OrderStatus.COMPLETED
        logger.info(f"Completed restaurant order {order_id}")

        if self._event_bus:
            self._event_bus.publish(
                OrderCompletedEvent(
                    correlation_id=str(order_id),
                    order_id=order.order_id,
                    tenant_id=order.tenant_id,
                    total_amount_cents=int(order.total_amount.amount * 100)
                )
            )

        return order


class KitchenDisplayService:
    """Service orchestrating Kitchen Display System (KDS) tickets."""

    def __init__(self) -> None:
        self._tickets: dict[UUID, KitchenTicket] = {}

    async def create_ticket(self, order: Order) -> KitchenTicket:
        """Generate kitchen ticket from placed order."""
        summary = [{"name": item.item_name, "qty": item.quantity} for item in order.items]
        ticket = KitchenTicket(
            order_id=order.order_id,
            table_number=order.table_number,
            items_summary=summary,
            status="QUEUED"
        )
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    async def update_ticket_status(self, ticket_id: UUID, status: str) -> KitchenTicket:
        """Update cooking status (QUEUED, COOKING, READY)."""
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise ValueError(f"Kitchen ticket {ticket_id} not found")
        ticket.status = status
        return ticket


class InventoryManagementService:
    """Service tracking ingredient inventory and stock levels."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._ingredients: dict[UUID, Ingredient] = {}
        self._event_bus = event_bus

    async def add_ingredient(self, ingredient: Ingredient) -> None:
        """Add or update an ingredient in inventory."""
        self._ingredients[ingredient.ingredient_id] = ingredient

    async def deduct_stock(self, ingredient_id: UUID, qty: float, tenant_id: str = "default") -> Ingredient:
        """Deduct stock and check low stock threshold."""
        ing = self._ingredients.get(ingredient_id)
        if not ing:
            raise ValueError(f"Ingredient {ingredient_id} not found")

        ing.current_stock -= qty
        if ing.current_stock <= ing.reorder_threshold and self._event_bus:
            self._event_bus.publish(
                IngredientLowEvent(
                    correlation_id=str(ing.ingredient_id),
                    tenant_id=tenant_id,
                    ingredient_id=ing.ingredient_id,
                    ingredient_name=ing.name,
                    current_stock=ing.current_stock,
                    reorder_threshold=ing.reorder_threshold
                )
            )
        return ing


class ReservationService:
    """Service managing customer dining reservations."""

    def __init__(self) -> None:
        self._reservations: dict[UUID, Reservation] = {}

    async def create_reservation(self, reservation: Reservation) -> Reservation:
        """Create table reservation."""
        self._reservations[reservation.reservation_id] = reservation
        return reservation


class FoodCostAnalyticsService:
    """Service performing Food Cost Percentage calculation and AI optimization."""

    @staticmethod
    def calculate_food_cost(total_revenue: Money, cogs: Money, target_cost_pct: float = 30.0) -> FoodCostAnalytics:
        """Calculate food cost percentage and generate recommendation."""
        if total_revenue.amount == Decimal("0.00"):
            pct = 0.0
        else:
            pct = float((cogs.amount / total_revenue.amount) * 100)

        rec = None
        if pct > target_cost_pct:
            rec = f"Food cost ({pct:.1f}%) exceeds target ({target_cost_pct:.1f}%). Recommend reducing portion sizes or re-negotiating supplier ingredient prices."

        return FoodCostAnalytics(
            total_revenue=total_revenue,
            total_cost_of_goods=cogs,
            food_cost_percentage=round(pct, 2),
            target_food_cost_percentage=target_cost_pct,
            recommendation=rec
        )
