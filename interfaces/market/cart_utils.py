from apps.orders.models import OrderItem

def get_order_item_creator_kwark_by_request(request):
    if request.user.is_authenticated:
        return {'user' : request.user}
    elif request.session:
        return {'session_id' : request.session.session_key}


def get_cart_queryset_by_request(request):
    return OrderItem.objects.filter(
        **get_order_item_creator_kwark_by_request(request),
        status=OrderItem.OrderItemStatus.CARD
    )


