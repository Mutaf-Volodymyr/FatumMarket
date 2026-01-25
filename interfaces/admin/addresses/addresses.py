from django.contrib import admin

from django.contrib import messages
from apps.address.models import Address
from apps.address.tasks import validate_and_geocode_address

@admin.action(description="🔁 Перепроверить и геокодировать")
def revalidate_addresses(modeladmin, request, queryset):
    for address in queryset:
        validate_and_geocode_address(address.id)

    messages.success(
        request,
        f"Запущена проверка для {queryset.count()} адресов"
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "raw_address",
        "city",
        "is_validated",
        "latitude",
        "longitude",
        'map_link',
    )

    list_filter = (
        "is_validated",
        "city",
    )

    search_fields = (
        "raw_address",
        "city",
        "street",
    )

    readonly_fields = (
        "latitude",
        "longitude",
        "is_validated",
        "validation_error",
        'map_link',
    )

    ordering = ("-id",)
    actions = [revalidate_addresses]

