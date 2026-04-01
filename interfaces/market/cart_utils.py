from decimal import Decimal

from django.db.models import OuterRef, Exists

from apps.orders.models import OrderItem


def get_order_item_creator_kwark_by_request(request):
    if request.user.is_authenticated:
        return {'user_id': request.user.id}
    elif request.session:
        if request.session.session_key is None:
            request.session.save()
        return {'session_id': request.session.session_key}


def get_cart_queryset_by_request(request):
    return OrderItem.objects.filter(
        **get_order_item_creator_kwark_by_request(request),
        status=OrderItem.OrderItemStatus.CARD
    )


def annotate_product_in_carts_by_request(request, product):
    cart_items = get_cart_queryset_by_request(request).\
        filter(product=OuterRef('pk'))

    return product.annotate(in_cart=Exists(cart_items))


def make_new_summary_price_context(cart_items, serializable=False ):
    total_price = Decimal('0.00')
    total_discount = Decimal('0.00')

    for item in cart_items:
        item_total = (item.price or item.product.price) * item.quantity
        total_price += item_total
        item_discount = (item.discount or Decimal('0.00')) * item.quantity
        total_discount += item_discount

    if serializable:
        return {
            'total_price': str(total_price),
            'total_discount': str(total_discount),
            'final_price': str(total_price - total_discount),
            'cart_count': str(cart_items.count()),
        }

    return {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': total_price - total_discount,
        'cart_count': cart_items.count(),
    }