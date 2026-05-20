from django.contrib import admin

from apps.delivery.models import PickupPlace


@admin.register(PickupPlace)
class PickupPlaceAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "position",
        "show_room",
    )
    list_editable = (
        "position",
        "show_room",
    )
    ordering = ("position",)
