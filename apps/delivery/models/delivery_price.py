from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel, PositionField, PriceField

__all__ = ["CourierDeliveryPrice"]


class CourierDeliveryPrice(BaseModel):

    city = CharField(max_length=50, verbose_name=_("Населенный пункт"), unique=True)
    cost = PriceField(null=False, blank=False)
    position = PositionField()

    class Meta:
        verbose_name = _("Стоимость курьерской доставки")
        verbose_name_plural = _("Стоимость курьерской доставки")
        db_table = "courier_delivery_cost"

    def __str__(self):
        return f"{self.city}: {self.cost}"
