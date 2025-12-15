from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from apps.delivery.models.delivery import Delivery
from django.utils.translation import gettext_lazy as _





@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'delivery_type',  'urgency', 'delivered_at', 'returned')
    list_filter = (
        # ("delivered_at", DateRangeFilter),
        # ("possible_delivery_time_from", DateRangeFilter),
        # ("possible_delivery_time_to", DateRangeFilter),
        'delivery_type', 'urgency', "returned", 'user',
    )
    readonly_fields = ['returned', 'delivered_at',]
