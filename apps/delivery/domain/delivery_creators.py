from abc import ABC, abstractmethod

from apps.address.models import Address
from apps.delivery.domain.schema import CreatePickupDeliverySchema, BaseCreateDeliverySchema, \
    CreateCourierDeliverySchema
from apps.delivery.models import Delivery
from apps.orders.models import Order
from apps.users.models import User


class OrderDeliveryException(Exception):
    pass


class BaseDeliveryCreator(ABC):
    _schema: BaseCreateDeliverySchema
    _type: str

    def __init__(self, *, order: Order, recipient: User, data: dict, address: Address = None):
        self._order = order
        self._recipient = recipient
        self._address = address
        self._delivery_instance = None
        self._delivery_schema = self._schema.model_validate(data)

    @abstractmethod
    def create(self):
        pass


class PickupDeliveryCreator(BaseDeliveryCreator):
    _schema = CreatePickupDeliverySchema
    _type = 'pickup'

    def create(self):
        if self._delivery_instance is not None:
            raise OrderDeliveryException("PickupDelivery already exists")

        delivery = Delivery.objects.create(
            order=self._order,
            recipient=self._recipient,
            **self._delivery_schema.model_dump(exclude_unset=True),
        )
        self._delivery_instance = delivery
        return self._delivery_instance


class CourierDeliveryCreator(BaseDeliveryCreator):
    _schema = CreateCourierDeliverySchema
    _type = 'courier'

    def create(self):
        if self._delivery_instance is not None:
            raise OrderDeliveryException("CourierDelivery already exists")
        if type(self._address) is not Address:
            raise OrderDeliveryException("CourierDelivery must have address")
        delivery = Delivery.objects.create(
            order=self._order,
            recipient=self._recipient,
            address=self._address,
            **self._delivery_schema.model_dump(exclude_unset=True),
        )
        self._delivery_instance = delivery
        return self._delivery_instance


class GeneralOrderDeliveryCreator:
    _creators = [
        PickupDeliveryCreator,
        CourierDeliveryCreator,
    ]

    def __init__(self, order: Order, delivery_type: str, recipient: User):
        self._order = order
        self._recipient = recipient
        self._creator_class = self._get_creator_class(delivery_type)

    def _get_creator_class(self, delivery_type):
        for creator in self._creators:
            if creator._type == delivery_type:
                return creator
        raise OrderDeliveryException('%s is not a valid delivery type' % delivery_type)

    def create_order_delivery(self, data):
        self.creator = self._creator_class(
            order=self._order,
            recipient=self._recipient,
            data=data,
        )
        self.delivery = self.creator.create()

        return self.delivery
