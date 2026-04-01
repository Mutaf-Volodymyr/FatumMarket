from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from apps.products.models import Category


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    readonly_fields = ("created_at", "updated_at", "parent", "products_count")
    mptt_indent_field = "name"
    list_display = ("tree_actions", "indented_title", "position")
    list_editable = ("position",)
    list_display_links = ("indented_title",)
