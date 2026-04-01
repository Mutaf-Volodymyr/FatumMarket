from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.orders.domain.order_item_card_manager import OrderItemCartManager, OrderItemException
from apps.orders.models import OrderItem
from interfaces.market.cart_utils import (
    get_cart_queryset_by_request,
    get_order_item_creator_kwark_by_request,
    make_new_summary_price_context,
)


def cart_view(request):
    cart_items = (
        get_cart_queryset_by_request(request)
        .select_related("product", "product__brand")
        .prefetch_related("product__images")
    )

    summary_price_context = make_new_summary_price_context(cart_items)

    return render(request, "market/cart.html", summary_price_context)


def cart_add_view(request, product_id):
    """Add product to cart"""
    if request.method == "POST":

        success = True
        error_message = None

        quantity = int(request.POST.get("quantity", 1))

        cart_queryset = get_cart_queryset_by_request(request)
        cart_item = cart_queryset.filter(product_id=product_id).first()

        try:
            if cart_item:
                manager = OrderItemCartManager(instance=cart_item)
                manager.update_quantity(quantity)
            else:
                manager = OrderItemCartManager(
                    data={
                        "quantity": quantity,
                        "product_id": product_id,
                        **get_order_item_creator_kwark_by_request(request),
                    }
                )
                manager.create_cart()

        except OrderItemException as e:
            error_message = str(e)
            success = False

        except Exception:
            error_message = "Неизвестная ошибка"
            success = False

        # Check if this is an AJAX request
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.content_type == "application/json"
        ):
            cart_count = get_cart_queryset_by_request(request).count()

            if success:
                return JsonResponse({"success": True, "cart_count": cart_count, "in_cart": True})
            else:
                return JsonResponse(
                    {"success": False, "error": error_message, "cart_count": cart_count}, status=400
                )

        if not success:
            messages.error(request, error_message)

        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        return redirect("market:home")

    return redirect("market:home")


def cart_remove_view(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(
        OrderItem,
        id=item_id,
        status=OrderItem.OrderItemStatus.CARD,
        **get_order_item_creator_kwark_by_request(request),
    )
    manager = OrderItemCartManager(instance=cart_item)
    manager.delete_cart()

    # Check if this is an AJAX request
    if (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.content_type == "application/json"
    ):
        cart_items = get_cart_queryset_by_request(request).select_related("product")

        summary_price_context = make_new_summary_price_context(cart_items, serializable=True)

        summary_price_context.update(
            {
                "success": True,
                "removed": True,
                "empty": cart_items.count() == 0,
                "message": "Товар удален из корзины",
            }
        )
        return JsonResponse(summary_price_context)

    messages.success(request, "Товар удален из корзины")
    return redirect("market:cart")


def cart_update_view(request, item_id):
    """Update cart item quantity"""
    if request.method == "POST":
        cart_item = get_object_or_404(
            OrderItem,
            id=item_id,
            status=OrderItem.OrderItemStatus.CARD,
            **get_order_item_creator_kwark_by_request(request),
        )
        quantity = int(request.POST.get("quantity", 1))

        try:
            manager = OrderItemCartManager(instance=cart_item)
            new_quantity = manager.update_quantity(quantity)

            success = True
            error_message = None
            removed = new_quantity == 0

        except OrderItemException as e:
            error_message = str(e)
            success = False
            removed = False

        # Check if this is an AJAX request
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.content_type == "application/json"
        ):
            cart_items = get_cart_queryset_by_request(request).select_related("product")

            summary_price_context = make_new_summary_price_context(cart_items, serializable=True)
            summary_price_context.update(
                {
                    "success": success,
                    "removed": removed,
                }
            )

            if success:
                return JsonResponse(summary_price_context)
            else:
                return JsonResponse({"success": success, "error": error_message}, status=400)

        if not success:
            messages.error(request, error_message)
        elif removed:
            messages.success(request, "Товар удален из корзины")

        return redirect("market:cart")

    return redirect("market:cart")
