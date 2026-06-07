from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from apps.delivery.models import PickupPlace
from apps.orders.domain.order_item_card_service import OrderItemCartService, OrderItemException
from apps.orders.schemas import OrderItemSchema
from interfaces.market.cart_utils import make_new_summary_price_context


def cart_view(request):
    service = OrderItemCartService(
        session_key=request.session.session_key,
        customer=request.user,
    )
    cart_items = (
        service.get_valid_queryset()
        .select_related("product", "product__brand")
        .prefetch_related("product__images")
    )

    summary_price_context = make_new_summary_price_context(cart_items)
    summary_price_context["pickup_places"] = PickupPlace.objects.all()

    return render(request, "market/cart.html", summary_price_context)


def cart_add_view(request, product_id):
    """Add product to cart or update quantity if exists"""
    if request.method == "POST":

        success = True
        error_message = None
        schema = OrderItemSchema(
            quantity=int(request.POST.get("quantity", 1)),
            product_id=product_id,
        )
        service = OrderItemCartService(
            session_key=request.session.session_key,
            customer=request.user,
        )
        try:
            service.create_cart(schema)
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
            cart_count = service.get_valid_queryset().count()

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
    service = OrderItemCartService(
        session_key=request.session.session_key,
        customer=request.user,
    )

    service.delete_cart(item_id)
    # Check if this is an AJAX request
    if (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.content_type == "application/json"
    ):
        cart_items = service.get_valid_queryset().select_related("product")

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
    service = OrderItemCartService(
        session_key=request.session.session_key,
        customer=request.user,
    )

    if request.method == "POST":

        quantity = int(request.POST.get("quantity", 1))

        try:

            new_quantity = service.update_quantity(quantity)

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
            cart_items = service.get_valid_queryset().select_related("product")

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
