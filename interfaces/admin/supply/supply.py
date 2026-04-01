from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter

from apps.supply.models import ProductSupply, Supplier, Supply


class SupplyProductInline(admin.StackedInline):
    model = ProductSupply
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    pass


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    inlines = [SupplyProductInline]
    list_display = ("__str__", "is_batch_paid", "sent_at", "received_at")
    list_filter = (
        "is_batch_paid",
        "import_coast",
        ("received_at", DateRangeFilter),
        ("sent_at", DateRangeFilter),
    )
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "supplier",
                    "is_import_paid",
                    "is_batch_paid",
                    "sent_at",
                    "received_at",
                ]
            },
        ),
        (_("Цены"), {"fields": ["import_coast", "batch_cost", "batch_revenue", "markup_percent"]}),
    )
    readonly_fields = ["batch_cost", "batch_revenue", "markup_percent"]
