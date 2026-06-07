from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models

from base.for_model import BaseModel
from base.micro_domains import FutureDatetime
from config import settings

__all__ = ["Fitting"]

if TYPE_CHECKING:
    from apps.delivery.models import PickupPlace
    from apps.products.models import Product


class FittingManager(models.Manager):

    def get_draft(
        self, *, user: settings.AUTH_USER_MODEL = None, session_key: str = None
    ) -> Any | None:
        if not user and not session_key:
            raise KeyError("User or session_key is required")

        if user:
            fitting = super().filter(user=user, status=self.model.FittingStatus.DRAFT).first()
            if fitting:
                return fitting

        if session_key:
            fitting = (
                super()
                .filter(session_key=session_key, status=self.model.FittingStatus.DRAFT)
                .first()
            )
            if fitting:
                return fitting

        return None

    def get_or_create_draft(
        self, *, user: settings.AUTH_USER_MODEL = None, session_key: str = None
    ) -> Any:
        fitting = self.get_draft(user=user, session_key=session_key)
        if fitting:
            return fitting
        return super().create(
            user=user, session_key=session_key, status=self.model.FittingStatus.DRAFT
        )


class Fitting(BaseModel):

    objects = FittingManager()

    class Meta:
        verbose_name = "Примерка"
        verbose_name_plural = "Примерки"
        db_table = "fittings"
        ordering = ("-date",)

    class FittingStatus(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PLANNED = "planned", "Запланировано"
        CANCELED = "canceled", "Отменён"
        HELD = "held", "Состоялась"

    show_room = models.ForeignKey(
        to="delivery.PickupPlace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Show Room",
        limit_choices_to={"show_room": True},
    )
    date = models.DateTimeField(verbose_name="Дата примерки", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="Клиент",
        related_name="fittings",
        null=True,
        blank=True,
    )
    session_key = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Сессия", db_index=True
    )
    status = models.CharField(
        max_length=100,
        default=FittingStatus.DRAFT,
        choices=FittingStatus.choices,
        verbose_name="Статус",
    )

    products = models.ManyToManyField(
        "products.Product",
        related_name="fittings",
        verbose_name="Товар",
        blank=True,
    )

    def __str__(self):
        return f"{self.date} - {self.status}"

    def add_product(self, product: Product):
        self.products.add(product)

    def remove_product(self, product: Product):
        self.products.remove(product)

    def confirm(
        self,
        *,
        date: FutureDatetime,
        show_room: PickupPlace,
        user: settings.AUTH_USER_MODEL = None,
    ):
        if self.status != self.FittingStatus.DRAFT:
            raise ValidationError("Only Draft Fitting can by confirmed.")
        if not show_room.show_room:
            raise ValidationError("Неверный Show Room.")

        user = self.user if self.user is not None else user

        if not user or user.is_anonymous:
            raise ValidationError("")

        self.status = self.FittingStatus.PLANNED
        self.user = user
        self.date = date
        self.show_room = show_room
        self.save(update_fields=["status", "user", "date", "show_room"])
        return self

    def cancel(self):
        if self.status is not self.FittingStatus.PLANNED:
            raise ValidationError("Only Planned Fitting can cancel.")
        self.status = self.FittingStatus.CANCELED
        self.save(update_fields=["status"])

    def held(self):
        if self.status is not self.FittingStatus.PLANNED:
            raise ValidationError("Only Planned Fitting can held.")
        self.status = self.FittingStatus.HELD
        self.save(update_fields=["status"])
