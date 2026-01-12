from django.contrib import admin
from django_google_maps.fields import AddressField
from django_google_maps.widgets import GoogleMapsAddressWidget

from apps.address.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    formfield_overrides = {
        AddressField: {'widget': GoogleMapsAddressWidget(attrs={'data-map-type': 'roadmap'})},
    }
