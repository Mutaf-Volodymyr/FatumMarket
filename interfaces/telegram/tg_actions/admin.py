from django.contrib import admin

from interfaces.telegram.tg_actions.models import ActionChat


@admin.register(ActionChat)
class ActionChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_authorized", "action_types")
    list_select_related = ("user",)
