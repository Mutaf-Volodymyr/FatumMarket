from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet

from apps.delivery.models import PickupPlace
from apps.fitting.models import Fitting
from apps.products.models import Product
from base.manager import BaseService

if TYPE_CHECKING:
    from apps.users.domain.customer_service import CustomerService
    from base.micro_domains import FutureDatetime


class DraftFittingException(Exception):
    pass


class DraftFittingService(BaseService):
    def __init__(
        self,
        *,
        session_key: str,
        customer_service: CustomerService = None,
        user: AbstractBaseUser = None,
    ):
        self.user = self._validate_user(user)
        self.session_key = session_key
        self._draft_fitting = None
        self._customer_service = customer_service

    @property
    def draft_fitting(self) -> Fitting:
        if self._draft_fitting is None:
            self._draft_fitting: Fitting = Fitting.objects.get_or_create_draft(
                user=self.user,
                session_key=self.session_key,
            )
        return self._draft_fitting

    def _get_product_or_error(self, pk: int):
        product = Product.objects.get_sale_product_by_pk(pk)
        if product is None:
            raise DraftFittingException("This product does not exist")
        return product

    def get_show_room_or_error(self, pk: int) -> PickupPlace:
        show_room = PickupPlace.objects.filter(pk=pk, show_room=True).first()
        if show_room is None:
            raise DraftFittingException("This room does not exist")
        return show_room

    def add_product(self, product_id: int) -> None:
        product = self._get_product_or_error(product_id)
        self.draft_fitting.add_product(product)

    def remove_product(self, product_id: int) -> None:
        product = self._get_product_or_error(product_id)
        self.draft_fitting.remove_product(product)

    def confirm_fitting(
        self,
        *,
        date: FutureDatetime,
        show_room_id: int,
    ) -> Fitting:
        draft = self.draft_fitting

        customer = (
            draft.user
            or self.user
            or (self._customer_service.user if self._customer_service else None)
        )
        if customer is None:
            raise DraftFittingException("This user does not exist")

        show_room = draft.show_room or self.get_show_room_or_error(show_room_id)

        draft.confirm(
            user=customer,
            date=date,
            show_room=show_room,
        )
        return draft

    def get_draft_fitting_products(self) -> QuerySet[Product]:
        return self.draft_fitting.products.all()  # type: ignore
