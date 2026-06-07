from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel, PriceField
from config import settings

__all__ = ["Delivery", "PickUpDelivery", "NovaPostaDelivery"]


class Delivery(BaseModel):

    class DeliveryTypeChoices(models.TextChoices):
        PICKUP = "pickup", _("Самовывоз")
        NOVA_POSTA = "nova_posta", _("Nova Posta")

    class ReturnChoices(models.TextChoices):
        FULL = "full", _("Полный")
        PARTIAL = "partial", _("Частичный")

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.PROTECT,
        verbose_name=_("Заказ"),
        related_name="delivery",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("Получатель"),
        null=True,
        blank=True,
    )
    delivery_type = models.CharField(
        max_length=100,
        choices=DeliveryTypeChoices.choices,
        verbose_name=_("Способ доставки"),
    )
    comment = models.TextField(null=True, blank=True, verbose_name=_("Комментарий"))

    # result
    is_delivered = models.BooleanField(default=False, verbose_name=_("Доставлено"))
    delivered_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Время доставки"), editable=False
    )
    returned = models.CharField(
        max_length=100,
        choices=ReturnChoices.choices,
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Возврат"),
    )

    class Meta:
        verbose_name = _("Доставка")
        verbose_name_plural = _("Доставки")
        db_table = "delivery"

    DEFAULT_DELIVERY_TYPE: DeliveryTypeChoices = None

    def __str__(self):
        is_delivered = "+" if self.is_delivered else "-"
        return f"[{self.order_id}] to {self.recipient} | {self.delivery_type}  | {is_delivered}"

    def _get_old_model(self):
        return Delivery.objects.get(pk=self.order.pk)

    def _set_delivered_at(self, old_model: "Delivery", update_fields: list[str]):
        if self.is_delivered and not old_model.is_delivered:
            self.delivered_at = datetime.now()
        return ["is_delivered", "delivered_at"] + update_fields

    def save(self, *args, **kwargs):
        if self.pk:
            update_fields = list(kwargs.pop("update_fields", []))
            old_model = self._get_old_model()
            update_fields_new = self._set_delivered_at(old_model, update_fields)
            if update_fields:
                update_fields += update_fields_new
                kwargs["update_fields"] = update_fields
        if self.DEFAULT_DELIVERY_TYPE and self.delivery_type != self.DEFAULT_DELIVERY_TYPE:
            self.delivery_type = self.DeliveryTypeChoices.DEFAULT_DELIVERY_TYPE
        super().save(*args, **kwargs)


class PickUpDelivery(Delivery):
    DEFAULT_DELIVERY_TYPE = Delivery.DeliveryTypeChoices.PICKUP

    pickup_place = models.ForeignKey(
        to="delivery.PickupPlace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Pickup Place",
        related_name="deliveries",
    )

    class Meta:
        verbose_name = _("Доставка [Самовывоз]")
        verbose_name_plural = _("Доставки [Самовывоз]")
        db_table = "delivery_pickup"


class NovaPostaDelivery(Delivery):
    DEFAULT_DELIVERY_TYPE = Delivery.DeliveryTypeChoices.NOVA_POSTA

    class Meta:
        verbose_name = _("Доставка [Nova Posta]")
        verbose_name_plural = _("Доставки [Nova Posta]")
        db_table = "delivery_nova_posta"

    class NovaPostaDeliveryTypeChoices(models.TextChoices):
        COURIER = "courier", _("Курьер")
        PARCEL_LOCKER = "parcel_locker", _("Поштомат")
        POST_OFFICE = "post_office", _("Отделение")

    address = models.ForeignKey(
        "address.Address", on_delete=models.PROTECT, verbose_name=_("Адрес"), null=True, blank=True
    )

    post_office = models.PositiveIntegerField(
        verbose_name=_("Номер почтового отделения"), null=True, blank=True
    )

    parcel_locker = models.PositiveIntegerField(
        verbose_name=_("Номер  почтомата"), null=True, blank=True
    )

    delivery_cost = PriceField(verbose_name=_("Стоимость доставки"), null=True, blank=True)
