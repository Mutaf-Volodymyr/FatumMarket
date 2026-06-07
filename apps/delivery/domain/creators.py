from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from django.db import IntegrityError

from apps.address.domain.address_service import AddressService
from apps.delivery.models import Delivery, NovaPostaDelivery, PickUpDelivery, PickupPlace
from apps.delivery.shemas import CreateNovaPostaDeliverySchema, CreatePickupDeliverySchema

if TYPE_CHECKING:
    from apps.delivery.shemas.create import CreateDeliverySchema
    from apps.orders.models import Order
    from apps.users.models import User


class DeliveryCreatorException(Exception):
    pass


class DeliveryCreator(ABC):

    @classmethod
    @abstractmethod
    def create_delivery(cls, *, schema: CreateDeliverySchema, order: Order, recipient: User):
        pass


class PickupDeliveryCreator(DeliveryCreator):
    _schema = CreatePickupDeliverySchema
    _type = Delivery.DeliveryTypeChoices.PICKUP.value
    _model = PickUpDelivery

    @classmethod
    def create_delivery(cls, *, schema: CreatePickupDeliverySchema, order: Order, recipient: User):
        cls.validate_pickup_place_id(schema.pickup_place_id)

        return cls._model.objects.create(
            delivery_type=cls._type,
            order=order,
            recipient=recipient,
            **schema.model_dump(exclude_none=True),
        )

    @classmethod
    def validate_pickup_place_id(cls, pickup_place_id: int):
        if not PickupPlace.objects.filter(id=pickup_place_id).exists():
            raise DeliveryCreatorException("Pickup place does not exist")


class NovaPostDeliveryCreator(DeliveryCreator):
    _schema = CreateNovaPostaDeliverySchema
    _type = Delivery.DeliveryTypeChoices.NOVA_POSTA.value
    _model = NovaPostaDelivery
    _address_service = AddressService

    @classmethod
    def create_delivery(
        cls, *, schema: CreateNovaPostaDeliverySchema, order: Order, recipient: User
    ):
        address = None
        if schema.address:
            address = cls._address_service.get_or_create_address(schema.address)
        return cls._model.objects.create(
            delivery_type=cls._type,
            order=order,
            recipient=recipient,
            address=address,
            **schema.model_dump(exclude_none=True),
        )


class GeneralOrderDeliveryCreator:
    _creators = [
        PickupDeliveryCreator,
        NovaPostDeliveryCreator,
    ]

    def __init__(self, order: Order, recipient: User):
        self._order = order
        self._recipient = recipient
        self._delivery_schema = None
        self._creator_class = None
        self._delivery = None
        self._logger = logging.getLogger(__name__)

    def _get_creator_class(self, delivery_schema):
        for creator in self._creators:
            if isinstance(delivery_schema, creator._schema):
                return creator
        raise DeliveryCreatorException("Unknown delivery type")

    def create_order_delivery(self, *, delivery_schema: CreateDeliverySchema):
        self._delivery_schema = delivery_schema
        self._creator_class = self._get_creator_class(delivery_schema)
        try:
            self.delivery = self._creator_class.create_delivery(  # type: ignore
                order=self._order,
                recipient=self._recipient,
                schema=delivery_schema,
            )
            return self.delivery

        except IntegrityError as e:
            self._logger.error(str(e))
            raise DeliveryCreatorException("Неизвестная ошибка создания доставки")
