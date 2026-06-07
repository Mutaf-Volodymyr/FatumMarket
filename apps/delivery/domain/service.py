from apps.delivery.domain.creators import GeneralOrderDeliveryCreator
from apps.delivery.models import Delivery
from apps.delivery.shemas.create import CreateDeliverySchema
from apps.orders.models import Order
from apps.users.domain.customer_service import CustomerService
from base.manager import BaseService


class DeliveryServiceException(Exception):
    pass


class DeliveryService(BaseService):
    def __init__(
        self,
        *,
        order: Order,
        recipient_service: CustomerService | None = None,
        order_creator_class=None,
    ):
        self._order = order
        self._recipient_service = recipient_service
        self._order_creator_class = order_creator_class or GeneralOrderDeliveryCreator
        self._delivery: Delivery | None = None
        self._recipient = None

    def create_delivery(self, delivery_schema: CreateDeliverySchema) -> Delivery:
        creator = self._order_creator_class(
            order=self._order,
            recipient=self.recipient,
        )
        creator.create_order_delivery(delivery_schema=delivery_schema)
        self._delivery = creator.delivery
        return self._delivery

    @property
    def recipient(self):
        if self._recipient is None:
            if self._recipient_service:
                self._recipient = self._recipient_service.user
            else:
                self._recipient = self._order.user

        return self._recipient
