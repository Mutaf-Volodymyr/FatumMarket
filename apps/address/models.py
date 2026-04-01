from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from base.for_model import BaseModel

__all__ = [
    "Address",
]


class Address(BaseModel):
    raw_address = models.CharField(max_length=512)

    city = models.CharField(max_length=128, blank=True)
    street = models.CharField(max_length=128, blank=True)
    house = models.CharField(max_length=32, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    is_validated = models.BooleanField(default=False)
    validation_error = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.raw_address

    class Meta:
        db_table = "address"
        verbose_name = _("Адрес")
        verbose_name_plural = _("Адреса")

    @property
    def map_link(self):
        if not self.latitude or not self.longitude:
            return "-"
        url = (
            f"https://www.openstreetmap.org/"
            f"?mlat={self.latitude}&mlon={self.longitude}#map=18/{self.latitude}/{self.longitude}"
        )
        return format_html('<a href="{}" target="_blank">🗺 карта</a>', url)
