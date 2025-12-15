from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product, ProductImage
from apps.supply.models import ProductSupply


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductSupplyInline(admin.StackedInline):
    model = ProductSupply
    extra = 0
    can_delete = False
    readonly_fields = [
        'supply',
        'purchase_price',
        "purchase_price_usd",
        "qty",

    ]
    def has_add_permission(self, request, obj=None):
        return False



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',  'is_active', 'qty', 'price', 'has_discount')
    fields = ('name', 'description', 'category', 'is_active', 'qty', 'price', 'old_price', 'discount')
    readonly_fields = ('discount',)
    list_filter = ('is_active', 'category',)
    search_fields = ('name', 'description')

    inlines = [
        ProductImageInline,
        ProductSupplyInline,
    ]


    def has_discount(self, product):
        return bool(product.has_discount)
    has_discount.boolean = True
    has_discount.short_description = 'Со скидкой'

