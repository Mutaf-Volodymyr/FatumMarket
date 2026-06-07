from django.contrib import admin

from apps.fitting.models import Fitting


class ProductFittingInline(admin.TabularInline):
    model = Fitting.products.through
    fields = ("product",)
    extra = 0
    verbose_name = "Товар"
    verbose_name_plural = "Товары"


@admin.register(Fitting)
class FittingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "date", "show_room")
    fields = [
        "date",
        "session_key",
        "user",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = ("user", "status", "show_room")
    readonly_fields = ("created_at", "updated_at", "session_key")

    autocomplete_fields = ("products", "user")
    inlines = (ProductFittingInline,)
