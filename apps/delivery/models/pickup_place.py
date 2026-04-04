from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel, PositionField

__all__ = ["PickupPlace"]


class PickupPlace(BaseModel):

    address = CharField(max_length=50, verbose_name=_("Адрес"))
    position = PositionField()

    class Meta:
        verbose_name = _("Место самовывоза")
        verbose_name_plural = _("Места самовывоза")
        db_table = "pickup_place"

    def __str__(self):
        return self.address
