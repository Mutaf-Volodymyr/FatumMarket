from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views import View

from apps.orders.domain.order_item_card_service import OrderItemCartService
from apps.orders.domain.order_service import OrderService, OrderServiceApiException
from apps.users.domain.customer_service import CustomerService
from interfaces.market.cart_utils import (
    get_customer_schema_by_request,
    get_delivery_schema_by_request,
    get_payment_schema_by_request,
    get_recipient_schema_by_request,
    make_new_summary_price_context,
)


class OrdersView(View):
    http_method_names = [
        "get",
        "post",
    ]

    def get(self, request, *args, **kwargs):
        cart_service = OrderItemCartService(
            session_key=request.session.session_key,
            customer=request.user,
        )
        cart_items = cart_service.get_valid_queryset().select_related("product")
        if not cart_items.exists():
            messages.error(request, "Корзина пуста")
            return redirect("market:cart")

        return render(request, "market/checkout.html", make_new_summary_price_context(cart_items))

    def post(self, request, *args, **kwargs):
        try:
            order_service = OrderService(
                session_key=request.session.session_key,
                user=request.user,
            )
            order = order_service.create_order(
                selected_cart_items=list(map(int, request.POST.getlist("selected_items", []))),
                customer_service=CustomerService(get_customer_schema_by_request(request)),
                delivery_schema=get_delivery_schema_by_request(request),
                payment_schema=get_payment_schema_by_request(request),
                recipient_service=CustomerService(get_recipient_schema_by_request(request)),
            )

            if request.user.is_authenticated:
                return redirect("market:order_success", order_id=order.id)
            else:
                return redirect("market:order_created")

        except Exception as e:
            messages.error(request, f"Ошибка оформления: {e}")
            return redirect("market:cart")


def order_detail_view(request, order_id):
    """Order detail page"""
    service = OrderService(
        user=request.user,  # type: ignore
        exception_class=OrderServiceApiException,
    )
    order = service.get_my_order(
        order_id,
        select_related=["user", "delivery", "payment"],
        prefetch_related=["items__product"],
    )

    return render(
        request,
        "market/order_detail.html",
        {
            "order": order,
        },
    )


def order_success_view(request, order_id):
    """Order success page"""
    service = OrderService(
        user=request.user,  # type: ignore
        exception_class=OrderServiceApiException,
    )
    try:
        order = service.get_my_order(order_id, select_related=["user", "delivery", "payment"])

        return render(
            request,
            "market/order_success.html",
            {
                "order": order,
            },
        )
    except OrderServiceApiException:
        return redirect("market:cart")


def order_created_view(request):
    return render(request, "market/order_created.html")


@login_required
def account_view(request):
    """User account page with order history"""
    service = OrderService(
        user=request.user,  # type: ignore
    )
    orders = service.get_my_orders()

    return render(
        request,
        "market/account.html",
        {
            "orders": orders,
        },
    )
