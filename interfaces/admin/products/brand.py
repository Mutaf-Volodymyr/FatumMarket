from apps.products.models.brand import Brand
from django.contrib import admin

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    pass

