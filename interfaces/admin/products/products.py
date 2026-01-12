from django.contrib import admin

from apps.orders.models import OrderItem
from apps.products.models import Product, ProductImage, ProductSpecification
from django.utils.translation import gettext_lazy as _
from apps.supply.models import ProductSupply


class SpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 0
    autocomplete_fields = (
        "specification_value",
    )


class ProductOrdersInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    verbose_name_plural = _('Заказы')
    verbose_name = _('Заказ')
    readonly_fields = ['order', 'price', 'quantity', 'created_at', 'updated_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductSupplyInline(admin.StackedInline):
    model = ProductSupply
    extra = 1
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
    fields = (
        'name',
        'description',
        'category',
        "brand",
        'is_active',
        'qty',
        'price',
        'old_price',
        'discount',
    )
    readonly_fields = ('discount',)
    list_filter = ('is_active', 'category', 'brand', "product_specification__specification_value__value")
    search_fields = ('name', 'description')

    inlines = [
        SpecificationInline,
        ProductImageInline,
        ProductSupplyInline,
        ProductOrdersInline,
    ]


    def has_discount(self, product):
        return bool(product.has_discount)
    has_discount.boolean = True
    has_discount.short_description = 'Со скидкой'

