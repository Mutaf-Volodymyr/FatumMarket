from decimal import Decimal
from typing import Optional, Iterable

from django.db import transaction

from apps.address.domain.address_manager import AddressManager
from apps.address.domain.schema import CreateAddressSchema
from apps.address.models import Address
from apps.delivery.domain.delivery_creators import GeneralOrderDeliveryCreator, OrderDeliveryException
from apps.delivery.models import Delivery
from apps.orders.domain.payment_manager import OrderPaymentManager
from apps.orders.domain.schema import OrderCreateSchema, PaymentSchema
from apps.orders.models import Order, OrderItem
from apps.users.domain.customer_manager import CustomerManager
from apps.users.domain.schema import UserSchema
from apps.users.models import User


class OrderCreatorException(Exception):
    pass


class OrderCreator:
    def __init__(
        self,
        *,
        carts: Iterable[OrderItem],
        order_data: Optional[dict] = None,
        customer_data: Optional[dict] = None,
        recipient_data: Optional[dict] = None,
        delivery_data: Optional[dict] = None,
        payment_data: Optional[dict] = None,
        session_id: Optional[str] = None,
    ):
        self._carts = list(carts)
        self._order_data = order_data or {}
        self._customer_data = customer_data or {}
        self._recipient_data = recipient_data or {}
        self._delivery_data = delivery_data or {}
        self._payment_data = payment_data or {}
        self._session_id = session_id

        if not self._carts:
            raise OrderCreatorException("Cart items are required to create order")

        self._order_schema = OrderCreateSchema.model_validate(self._order_data)
        self._customer = None
        self._recipient = None
        self._address = None
        self._order = None

    @transaction.atomic
    def create(self) -> Order:
        self._customer = self._resolve_customer(self._customer_data)
        self._recipient = self._resolve_recipient(self._recipient_data, self._customer)
        self._address = self._resolve_address(self._delivery_data, self._customer)

        self._order = self._create_order_instance()
        self._attach_cart_items(self._order)
        self._create_delivery(self._order, self._recipient, self._delivery_data, self._address)
        self._create_payment(self._order, self._payment_data)

        return self._finalizate(self._order)

    def _build_user_schema(self, data: dict) -> UserSchema:
        def _clean(value):
            if value is None:
                return None
            if isinstance(value, str):
                value = value.strip()
                return value or None
            return value

        phone_value = _clean(data.get("phone"))
        if phone_value is not None:
            phone_value = str(phone_value)
        email_value = _clean(data.get("email"))
        if email_value is not None:
            email_value = str(email_value)
        return UserSchema.model_validate({
            "id": data.get("id"),
            "email": email_value,
            "first_name": _clean(data.get("first_name")),
            "last_name": _clean(data.get("last_name")),
            "phone": phone_value,
        })

    def _resolve_customer(self, data: dict) -> User:
        if not data.get("phone") and not data.get("email"):
            raise OrderCreatorException("Customer phone or email is required")
        schema = self._build_user_schema(data)
        customer = CustomerManager.get_or_create_customer(schema)
        if customer is None:
            raise OrderCreatorException("Unable to resolve customer")
        return customer

    def _resolve_recipient(self, data: dict, customer: User) -> User:
        if not data:
            return customer
        if not data.get("phone") and not data.get("email"):
            raise OrderCreatorException("Recipient phone or email is required")
        schema = self._build_user_schema(data)
        recipient = CustomerManager.get_or_create_customer(schema)
        if recipient is None:
            raise OrderCreatorException("Unable to resolve recipient")
        return recipient

    def _resolve_address(self, data: dict, customer: User) -> Optional[Address]:
        delivery_type = data.get("delivery_type")
        if delivery_type != Delivery.DeliveryTypeChoices.courier:
            return None

        raw_address = data.get("raw_address")
        if isinstance(raw_address, str):
            raw_address = raw_address.strip()
        if not raw_address:
            raise OrderCreatorException("Courier delivery requires address")

        address_schema = CreateAddressSchema.model_validate({
            "raw_address": raw_address,
        })
        address = AddressManager.get_or_create_address(address_schema)
        AddressManager(instance=address).associate_with_user(customer)
        return address

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
            "user": self._customer,
            "status": Order.OrderStatus.DRAFT,
            "total_price": total_price,
            "total_discount": total_discount,
            "comment": self._order_schema.comment,
            "additional_data": self._order_schema.additional_data,
        }
        if self._session_id:
            order_kwargs["session_id"] = self._session_id

        return Order.objects.create(**order_kwargs)

    def _attach_cart_items(self, order: Order) -> None:
        OrderItem.objects.filter(id__in=[item.id for item in self._carts]).update(
            order=order,
            status=OrderItem.OrderItemStatus.ORDER,
            user=order.user,
        )

    def _create_delivery(self, order: Order, recipient: User, data: dict, address) -> None:
        delivery_type = data.get("delivery_type", Delivery.DeliveryTypeChoices.pickup)
        delivery_cost = data.get("delivery_cost")
        if isinstance(delivery_cost, str):
            delivery_cost = Decimal(delivery_cost) if delivery_cost else None

        delivery_payload = {
            "delivery_type": delivery_type,
            "recipient_id": recipient.id,
            "comment": data.get("comment"),
            "delivery_cost": delivery_cost,
        }

        creator = GeneralOrderDeliveryCreator(order, delivery_type, recipient)
        try:
            creator.create_order_delivery(delivery_payload, address=address)
        except OrderDeliveryException as exc:
            raise OrderCreatorException(str(exc)) from exc

    def _create_payment(self, order: Order, data: dict) -> None:
        if not data:
            return
        payment_schema = PaymentSchema.model_validate(data)
        payment_manager = OrderPaymentManager(order, payment_schema)
        payment_manager.create_order_payment()
        payment_manager.save_payment()

    def _finalizate(self, order: Order) -> None:
        order.status = Order.OrderStatus.IN_WORK
        order.save()
        return order












    #
    # def _save_order_to_db(self):
    #     self.order.total_price = self._order_total_price
    #     self.order.total_discount = self._order_total_discount
    #     self.order.status = Order.OrderStatus.IN_WORK
    #     self.order.save()
    #
    #
    # def _save_order_items_to_db(self):
    #     OrderItem.objects.bulk_create(self._order_items_instances)
    #     self.product_manager.update_queryset_quantity()
    #
    #
    # @property
    # def order(self):
    #     if self._order_instance is not None:
    #         return self._order_instance
    #     return self.create_order_instance()
    #
    # def create_order_instance(self):
    #     self._order_instance = Order(
    #         customer =self.customer_manager.customer,
    #         status=Order.OrderStatus.DRAFT,
    #         comment=self.order_schema.comment,
    #     )
    #     return self._order_instance
    #
    # @property
    # def order_items(self):
    #     if self._order_items_instances:
    #         return self._order_items_instances
    #     return self._create_order_item_instances()
    #
    # def _create_order_item_instances(self):
    #     for item_schema in self.order_schema.items:
    #         product = self.product_manager.get_product_by_id(item_schema.product_id)
    #
    #         order_item = OrderItem(
    #                 product=product,
    #                 order = self.order,
    #                 quantity = item_schema.quantity,
    #                 price = product.price,
    #                 discount = product.discount,
    #                 product_name = product.name,
    #             )
    #         self.product_manager.update_product_quantity(
    #             product_id=product.id,
    #             sale_qty=item_schema.quantity,
    #         )
    #
    #         self._order_items_instances.append(order_item)
    #
    #         self._update_order_total_prices(order_item)
    #
    #     return self._order_items_instances
    #
    #
    #
    # def _update_order_total_prices(self, order_item: OrderItem):
    #     quantity = order_item.quantity
    #     self._order_total_price += (order_item.price * quantity)
    #     self._order_total_discount += (order_item.discount * quantity)
    #
    #
    #
    # def create_order(self):
    #     with transaction.atomic():
    #         self._create_order_item_instances()
    #         self._save_order_to_db()
    #         self._save_order_items_to_db()
    #         self.create_delivery()
    #         self.create_payment()
    #
    #
    # def create_delivery(self):
    #     manager = OrderDeliveryManager(
    #         order = self.order,
    #         delivery_schema = self.order_schema.delivery,
    #     )
    #     manager.save_delivery()
    #
    # def create_payment(self):
    #     manager = OrderPaymentManager(
    #         order = self.order,
    #         payment_schema = self.order_schema.payment,
    #     )
    #     manager.create_order_payment()
