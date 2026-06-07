from __future__ import annotations

from typing import TYPE_CHECKING

from apps.orders.models import OrderItem
from apps.products.models import Product
from base.manager import BaseService

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.orders.schemas import OrderItemSchema
    from apps.users.backends import User


class OrderItemException(Exception):
    pass


class OrderItemCartService(BaseService):
    _class_model = OrderItem

    def __init__(
        self,
        session_key: str,
        customer: User | None = None,
        instance: OrderItem | None = None,
    ):
        self._customer = self._validate_user(customer)
        self._instance = instance
        self._session_key = session_key
        self._product = instance.product if instance else None
        self._schema = None

    def get_item_source_kwargs(self) -> dict:
        if self._customer is not None:
            return {"user": self._customer}
        return {"session_key": self._session_key}

    @property
    def product(self):
        if self._product is None:
            if self._schema:
                pk = self._schema.product_id
            elif self.instance:
                pk = self.instance.product_id
            else:
                pk = None
            self._product = Product.objects.get(
                pk=pk,
                is_active=True,
            )

        return self._product

    @property
    def instance(self):
        if self._instance is None:
            raise OrderItemException("Экземпляр не существует")

        return self._instance

    def create_cart(self, schema: OrderItemSchema):
        self._schema = schema
        self._validate_quantity(schema.quantity)

        self._instance, created = self._class_model.objects.get_or_create(
            **self.get_item_source_kwargs(),
            product_id=schema.product_id,
            status=self._class_model.OrderItemStatus.CARD,
            defaults={
                "quantity": schema.quantity,
            },
        )
        if created:
            self._logger.info("Created cart item: %s", self._instance)
            return self._instance

        self.update_quantity(schema.quantity)
        return self._instance

    def update_quantity(self, value: int):
        self._validate_quantity(value)

        if value <= 0:
            return self.delete_cart()

        self.instance.quantity = value
        self.instance.save(update_fields=["quantity"])

        self._logger.debug("Updated cart item qty: %s", self._instance)

        return value

    def delete_cart(self, item_id: int = None):
        if item_id is not None:
            self.get_instance_by_id(item_id)

        self.instance.delete()
        self._logger.info("Deleted cart item: %s", self.instance)

    def _validate_quantity(self, new_quantity: int):
        if new_quantity <= 0 or new_quantity > self.product.quantity:
            raise OrderItemException(
                "Недостаточно товара на складе. Доступно: %s", self.product.quantity
            )

    def get_instance_by_id(self, item_id: int):
        try:
            self._instance = self.get_valid_queryset().get(pk=item_id)
        except self._class_model.DoesNotExist:
            raise OrderItemException("Карточка не найдена")

    def get_valid_queryset(self) -> QuerySet:
        if self._customer:
            filters = {"user": self._customer}
        else:
            filters = {"session_key": self._session_key}
        return self._class_model.objects.filter(
            status=self._class_model.OrderItemStatus.CARD, **filters
        )

    def get_selected_cart_items_queryset(self, selected_items: list[int], validate=False):
        queryset = self.get_valid_queryset().select_related("product").filter(id__in=selected_items)
        if validate:
            self._validate_selected_cart_items_queryset(selected_items, queryset)
        return queryset

    def _validate_selected_cart_items_queryset(self, selected_items: list[int], queryset):
        if (not len(selected_items)) or len(selected_items) != queryset.count():
            raise OrderItemException("Выбранные товары не добавлены в корзину")
