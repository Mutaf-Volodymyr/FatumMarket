from django.contrib import admin

from apps.products.models.brand import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass
