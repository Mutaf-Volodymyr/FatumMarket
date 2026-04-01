from interfaces.market.cart_utils import get_cart_queryset_by_request


def cart_count(request):
    """Context processor to add cart count to all templates"""

    return {"cart_count": get_cart_queryset_by_request(request).count()}
