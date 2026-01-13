from apps.delivery.domian.schema import DeliverySchema
from apps.delivery.models import Delivery
from apps.orders.models import Order


class OrderDeliveryException(Exception):
    pass

class OrderDeliveryManager:
    def __init__(self, order: Order, delivery_schema: DeliverySchema):
        self._order = order
        self._delivery_schema = delivery_schema
        self._delivery = delivery_schema

    @property
    def delivery(self):
        if self._delivery is not None:
            self.create_order_delivery()
        return self._delivery

    def save_delivery(self):
        self.delivery.save()

    def create_order_delivery(self):
        self._delivery = Delivery(
            order=self._order,
            **self._delivery_schema.model_dump(exclude_unset=True),
        )

        return self._delivery