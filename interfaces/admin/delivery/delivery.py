from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from apps.delivery.models.delivery import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "delivery_type", "delivered_at", "returned")
    list_filter = (
        ("delivered_at", DateRangeFilter),
        "delivery_type",
        "returned",
        "recipient",
    )
    readonly_fields = [
        "returned",
        "delivered_at",
    ]
