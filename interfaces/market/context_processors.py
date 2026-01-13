from apps.orders.models import OrderItem


def cart_count(request):
    """Context processor to add cart count to all templates"""
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = OrderItem.objects.filter(
            user=request.user,
            status=OrderItem.OrderItemStatus.CARD
        ).count()
    return {'cart_count': cart_count}


