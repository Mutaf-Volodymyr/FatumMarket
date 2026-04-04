from django.contrib import admin

from apps.products.models import ProductImage, ProductImageThrough


class ProductImageThroughInline(admin.TabularInline):
    model = ProductImageThrough
    extra = 1
    fields = ("product", "position")
    autocomplete_fields = ("product",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    inlines = (ProductImageThroughInline,)
