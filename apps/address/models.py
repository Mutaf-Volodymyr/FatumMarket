from django_google_maps.fields import AddressField, GeoLocationField
from django.utils.translation import gettext_lazy as _
from base.for_model import BaseModel

__all__ = [
    'Address',
]

class Address(BaseModel):
    address = AddressField(max_length=200, verbose_name=_("Адрес"))
    geolocation = GeoLocationField(max_length=100, verbose_name=_('Геолокация'))



    def __str__(self):
        return self.address

    class Meta:
        db_table = 'address'
        verbose_name = _("Адрес")
        verbose_name_plural = _('Адреса')
