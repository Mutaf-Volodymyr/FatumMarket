from django.db.models import BooleanField, CharField, ImageField
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel, PositionField

__all__ = ["PickupPlace"]


def get_upload_path(instance, filename):
    return f"showrooms/{instance.id}/{filename}"


class PickupPlace(BaseModel):

    address = CharField(max_length=50, verbose_name=_("Адрес"))
    position = PositionField()
    show_room = BooleanField(default=False, verbose_name="Show Room")
    image = ImageField(
        upload_to=get_upload_path, verbose_name=_("Изображение"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Место самовывоза")
        verbose_name_plural = _("Места самовывоза")
        db_table = "pickup_place"

    def __str__(self):
        return self.address
