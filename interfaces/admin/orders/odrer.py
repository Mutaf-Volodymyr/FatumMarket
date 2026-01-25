from django.contrib import admin
from apps.delivery.models import Delivery
from apps.orders.models import Order, OrderPayment, OrderItem


class OrderPaymentInline(admin.StackedInline):
    model = OrderPayment
    can_delete = False
    can_edit = False
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    can_delete = False
    can_edit = False
    extra = 0
    fields = [
        'product',
        'quantity',
        'price',
        'discount'
    ]
    readonly_fields = fields


class DeliveryInline(admin.StackedInline):
    model = Delivery
    can_delete = False
    can_edit = False
    extra = 0
    readonly_fields = Delivery.get_fields_list()





@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'status', 'total_price')
    fields = [
        'user',
        'total_price',
        'total_discount',
        'comment',
        'status'
    ]
    list_filter = ('user', 'status', 'items__product',
                   'delivery__delivery_type', 'delivery__is_delivered',
                   "payment__payment_status", "payment__payment_method",
                   )

    readonly_fields = Order.get_fields_list()

    inlines = (OrderItemInline, DeliveryInline, OrderPaymentInline)

@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    pass