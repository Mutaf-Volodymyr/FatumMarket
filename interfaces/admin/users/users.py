from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.orders.models import OrderItem
from apps.users.models import User


class CardInlines(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    can_edit = False
    verbose_name_plural = _("Корзина")
    verbose_name = _("Корзина")

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        user = request.user
        return OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.CARD)


class UserOrderItemInlines(CardInlines):
    verbose_name_plural = _("Покупки")
    verbose_name = _("Покупки")

    def get_queryset(self, request):
        user = request.user
        return OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.ORDER)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "phone",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_baned",
        "last_login",
    )
    list_display_links = ("id", "first_name", "last_name")
    search_fields = ("phone", "email", "first_name", "last_name")
    list_filter = (
        "is_staff",
        "staff_status",
        "is_active",
        "is_baned",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                ),
            },
        ),
        (_("Права"), {"fields": ("groups", "user_permissions"), "classes": ("collapse",)}),
        (
            _("Контакты"),
            {"fields": ("phone", "email", "telegram_id", "addresses"), "classes": ("collapse",)},
        ),
        (
            _("Статусы"),
            {
                "fields": ("is_active", "is_baned", "is_staff", "staff_status"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Важные даты"),
            {
                "fields": (
                    "date_joined",
                    "last_login",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2", "status"),
            },
        ),
    )
    inlines = (
        CardInlines,
        UserOrderItemInlines,
    )
