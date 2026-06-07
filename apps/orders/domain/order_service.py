from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.exceptions import APIException

from apps.delivery.shemas.create import CreateDeliverySchema
from apps.orders.domain.order_creator import OrderCreator
from apps.orders.domain.order_item_card_service import OrderItemCartService
from apps.orders.models import Order
from apps.orders.schemas import PaymentSchema
from base.manager import BaseService

if TYPE_CHECKING:
    from django.db.models import Prefetch, QuerySet

    from apps.users.domain.customer_service import CustomerService
    from apps.users.models import User


class OrderServiceException(Exception):
    pass


class OrderServiceApiException(APIException):
    status_code = 400


class OrderService(BaseService):
    _order_creator_class = OrderCreator
    _order_items_service_class = OrderItemCartService
    _class_model = Order

    def __init__(
        self,
        *,
        session_key: str = None,
        customer_service: CustomerService = None,
        user: User = None,
        exception_class=OrderServiceException,
    ):

        self._customer = self._validate_user(user)
        self._session_key = session_key
        self._customer_service = customer_service
        self._exception_class = exception_class
        self._order = None

    def get_my_orders(self) -> QuerySet[Order]:
        if not self._customer:
            return Order.objects.none()
        return (
            Order.objects.filter(user=self._customer)
            .select_related("delivery", "payment")
            .prefetch_related("items")
            .order_by("-created_at")
        )

    def get_my_order(
        self,
        pk: int,
        select_related: list[str] = None,
        prefetch_related: list[str | Prefetch] = None,
    ) -> Order:

        if not self._customer:
            raise self._exception_class("Клиент не авторизирован")

        queryset = Order.objects

        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        order = queryset.filter(pk=pk, user=self._customer).first()

        if not order:
            raise self._exception_class("Заказ не найден")
        self._order = order

        return order

    def create_order(
        self,
        *,
        selected_cart_items: list[int],
        customer_service: CustomerService,
        delivery_schema: CreateDeliverySchema,
        payment_schema: PaymentSchema,
        recipient_service: CustomerService | None = None,
    ):
        order_item_cart_service = self._order_items_service_class(
            customer=self._customer,
            session_key=self._session_key,
        )
        carts = order_item_cart_service.get_selected_cart_items_queryset(
            selected_items=selected_cart_items, validate=True
        )
        creator = self._order_creator_class(
            carts=carts,
            customer_service=customer_service,
            delivery_schema=delivery_schema,
            payment_schema=payment_schema,
            recipient_service=recipient_service,
            customer=self._customer,
        )
        return creator.create()
