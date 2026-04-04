from django.contrib import admin

from apps.delivery.models import CourierDeliveryPrice


@admin.register(CourierDeliveryPrice)
class CourierDeliveryPriceAdmin(admin.ModelAdmin):
    list_display = ("city", "cost", "position")
    list_editable = ("cost", "position")
    ordering = ("position",)
