from datetime import datetime

from django.db import models
from base.for_model import BaseModel, PriceField
from django.utils.translation import gettext_lazy as _
from config import settings

__all__ = ['Delivery']

class Delivery(BaseModel):
    class DeliveryTypeChoices(models.TextChoices):
        pickup = 'pickup', _('Самовывоз')
        courier = 'courier', _('Курьер')
        nova_posta = 'nova_posta', _('Nova Posta')

    class SpeedChoices(models.TextChoices):
        URGENCY = 'quickly', _("Срочно")
        STANDARD = "standard", _("Стандартно")

    class ReturnChoices(models.TextChoices):
        FULL = 'full', _('Полный')
        PARTIAL = 'partial', _('Частичный')


    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.PROTECT,
        verbose_name=_('Заказ'),
        related_name='delivery',
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('Получатель'),
        null=True,
        blank=True,
    )
    unknown_recipient = models.TextField(null=True, blank=True, verbose_name=_("Неизвестный получатель"))

    # куда
    delivery_type = models.CharField(max_length=100, choices=DeliveryTypeChoices.choices, default=DeliveryTypeChoices.pickup, verbose_name=_('Способ доставки'),)
    address = models.ForeignKey('address.Address', on_delete=models.PROTECT, verbose_name=_('Адрес'), null=True, blank=True)
    comment = models.TextField(null=True, blank=True, verbose_name=_('Комментарий'))

    # когда
    urgency = models.CharField(max_length=100, choices=SpeedChoices.choices, default=SpeedChoices.STANDARD, verbose_name=_('Срочность'))
    possible_delivery_time_from = models.DateTimeField(
        verbose_name=_("Доставка от"),
        null=True, blank=True,
        help_text=_('Желаемое время доставки указанное клиентом')
    )
    possible_delivery_time_to = models.DateTimeField(
        verbose_name=_("Доставка до"),
        null=True, blank=True,
        help_text=_('Желаемое время доставки указанное клиентом')
    )

    # how money
    delivery_cost = PriceField(verbose_name=_('Стоимость доставки'))

    # result
    is_delivered = models.BooleanField(default=False, verbose_name=_('Доставлено'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Время доставки'), editable=False)
    returned = models.CharField(
        max_length=100,
        choices=ReturnChoices.choices,
        null=True, blank=True, editable=False,
        verbose_name=_('Возврат')
    )


    class Meta:
        verbose_name = _("Доставка")
        verbose_name_plural = _('Доставки')
        db_table = "delivery"

    def __str__(self):
        is_delivered = "+" if self.is_delivered else '-'
        return f"[{self.order_id}] to {self.user} | {self.delivery_type}  | {is_delivered}"


    def _get_old_model(self):
        return Delivery.objects.get(pk=self.order.pk)

    def _set_delivered_at(self, old_model, update_fields):
        if self.is_delivered and not old_model.is_delivered:
            self.delivered_at = datetime.now()
        return ['is_delivered', 'delivered_at']

    def save(self, *args, **kwargs):
        if self.pk:
            update_fields = list(kwargs.pop('update_fields', []))
            old_model = self._get_old_model()
            update_fields_new = self._set_delivered_at(old_model, update_fields)
            if update_fields:
                update_fields += update_fields_new
                kwargs['update_fields'] = update_fields
        super().save(*args, **kwargs)

