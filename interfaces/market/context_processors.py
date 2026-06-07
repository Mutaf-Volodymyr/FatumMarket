from apps.fitting.domain import DraftFittingService
from apps.orders.domain.order_item_card_service import OrderItemCartService


def cart_context(request):
    service = OrderItemCartService(
        customer=request.user,
        session_key=request.session.session_key,
    )
    product_ids = list(service.get_valid_queryset().values_list("product_id", flat=True))
    return {
        "cart_count": len(product_ids),
        "cart_product_ids": product_ids,
    }


def fitting_context(request):
    service = DraftFittingService(
        user=request.user,
        session_key=request.session.session_key,
    )
    product_ids = list(service.get_draft_fitting_products().values_list("id", flat=True))
    return {
        "fitting_count": len(product_ids),
        "fitting_product_ids": product_ids,
    }
