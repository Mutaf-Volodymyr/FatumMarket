from django.contrib import admin
from apps.users.models import User
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", 'first_name', 'last_name', 'is_staff', 'is_active', 'is_baned', 'last_login')
    list_display_links = ("id", "first_name", "last_name")
    search_fields = ('phone', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', "staff_status", 'is_active', 'is_baned', )

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name',),
        }),
        (_('Права'), {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Контакты'), {
            'fields': ('phone', 'email', 'telegram_id', 'addresses'),
            'classes': ('collapse',)
        }),
        (_("Статусы"), {
            'fields': ('is_active', 'is_baned', 'is_staff', "staff_status"),
            'classes': ('collapse',)
        }),
        (_("Важные даты"), {
            'fields': ('date_joined', 'last_login',),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'status'),
        }),
    )



