from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

from apps.delivery.domain.service import DeliveryService
from apps.orders.domain.payment_service import OrderPaymentService
from apps.orders.models import Order, OrderItem
from apps.users.domain.customer_service import CustomerService

if TYPE_CHECKING:
    from typing import Iterable

    from apps.delivery.shemas.create import CreateDeliverySchema
    from apps.orders.schemas import PaymentSchema
    from apps.users.models import User


class OrderCreatorException(Exception):
    pass


class OrderCreator:
    _delivery_service_class = DeliveryService
    _payment_service_class = OrderPaymentService

    def __init__(
        self,
        *,
        carts: Iterable[OrderItem],
        customer_service: CustomerService,
        delivery_schema: CreateDeliverySchema,
        payment_schema: PaymentSchema,
        customer: User | None = None,
        recipient_service: CustomerService | None = None,
    ):
        self._customer = self.__validate_customer(customer)
        self._carts = self.__validate_order_cards(carts)

        self._customer_service = customer_service
        self.recipient_service = recipient_service

        self._delivery_schema = delivery_schema
        self._delivery_service = None

        self._payment_schema = payment_schema
        self._payment_service = None

        self._order = None

    @transaction.atomic
    def create(self) -> Order:
        self._create_order_instance()
        self._attach_cart_items()
        self._create_delivery()
        self._create_payment()
        return self._finalizate()

    def __validate_order_cards(self, cards: Iterable[OrderItem]):
        if not cards:
            raise OrderCreatorException("Cart items are required to create order")
        return list(cards)

    def __validate_customer(self, customer):
        if customer is None:
            return None
        if customer.is_anonymous:
            return None
        return customer

    @property
    def customer(self):
        if self._customer is None:
            self._customer = self._customer or self._customer_service.user
        return self._customer

    def get_delivery_service(self):
        if self._delivery_service is None:
            self._delivery_service = self._delivery_service_class(
                order=self._order,
                recipient_service=self.recipient_service,
            )
        return self._delivery_service

    def get_payment_service(self):
        if self._payment_service is None:
            self._payment_service = self._payment_service_class(
                order=self._order,
            )
        return self._payment_service

    def _calculate_totals(self) -> tuple[Decimal, Decimal]:
        total_price = Decimal("0.00")
        total_discount = Decimal("0.00")

        for item in self._carts:
            item_total = (item.price or item.product.price) * item.quantity
            total_price += item_total
            item_discount = (item.discount or Decimal("0.00")) * item.quantity
            total_discount += item_discount

        return total_price, total_discount

    def _create_order_instance(self) -> Order:
        total_price, total_discount = self._calculate_totals()

        order_kwargs = {
            "user": self.customer,
            "status": Order.OrderStatus.DRAFT,
            "total_price": total_price,
            "total_discount": total_discount,
        }

        self._order = Order.objects.create(**order_kwargs)
        return self._order

    def _attach_cart_items(self) -> None:
        OrderItem.objects.filter(id__in=[item.id for item in self._carts]).update(
            order=self._order,
            status=OrderItem.OrderItemStatus.ORDER,
            user=self._order.user,
        )

    def _create_delivery(self) -> None:
        service = self.get_delivery_service()
        service.create_delivery(delivery_schema=self._delivery_schema)

    def _create_payment(self) -> None:
        service = self.get_payment_service()
        service.create(payment_schema=self._payment_schema)

    def _finalizate(self) -> Order:
        self._order.status = Order.OrderStatus.IN_WORK
        self._order.save(update_fields=["status"])
        return self._order

    #
