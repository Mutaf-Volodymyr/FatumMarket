from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from pydantic import ValidationError

from apps.delivery.domain.delivery_creators import OrderDeliveryException
from apps.delivery.models import Delivery
from apps.orders.domain.order_creator import OrderCreator, OrderCreatorException
from apps.orders.models import Order
from interfaces.market.cart_utils import (
    get_cart_queryset_by_request,
    get_order_item_creator_kwark_by_request,
)


def checkout_view(request):
    """Checkout page - create order from cart items"""
    cart_items = get_cart_queryset_by_request(request).select_related("product")

    if not cart_items.exists():
        messages.error(request, "Корзина пуста")
        return redirect("market:cart")

    if request.method == "POST":
        selected_items = request.POST.getlist("selected_items")

        if not selected_items:
            return redirect("market:cart")

        try:
            selected_cart_items = (
                get_cart_queryset_by_request(request)
                .filter(
                    id__in=selected_items,
                )
                .select_related("product")
            )

            if not selected_cart_items.exists():
                messages.error(request, "Выбранные товары не найдены")
                return redirect("market:cart")

            def _clean_optional(value):
                if value is None:
                    return None
                if isinstance(value, str):
                    value = value.strip()
                    return value or None
                return value

            def _split_name(full_name):
                parts = full_name.split()
                first_name = parts[0] if parts else ""
                last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
                return first_name, last_name

            delivery_type = request.POST.get(
                "delivery_type",
                Delivery.DeliveryTypeChoices.pickup,
            )
            if delivery_type == Delivery.DeliveryTypeChoices.nova_posta:
                delivery_type = Delivery.DeliveryTypeChoices.pickup

            order_data = {"comment": _clean_optional(request.POST.get("comment"))}

            if request.user.is_authenticated:
                customer_data = {
                    "id": request.user.id,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                    "phone": request.user.phone,
                }
            else:
                customer_name = _clean_optional(request.POST.get("customer_name", "")) or ""
                customer_phone = _clean_optional(request.POST.get("customer_phone", "")) or ""
                first_name, last_name = _split_name(customer_name)
                customer_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": customer_phone,
                }

            recipient_data = {}
            recipient_note = ""
            if request.user.is_authenticated:
                recipient_type = request.POST.get("recipient_type", "self")
                if recipient_type == "other":
                    recipient_name = _clean_optional(request.POST.get("recipient_name", "")) or ""
                    recipient_phone = _clean_optional(request.POST.get("recipient_phone", "")) or ""
                    if recipient_phone:
                        from apps.users.models import User as UserModel

                        existing = UserModel.objects.filter(phone=recipient_phone).first()
                        if existing:
                            recipient_data = {
                                "id": existing.id,
                                "email": existing.email,
                                "first_name": existing.first_name,
                                "last_name": existing.last_name,
                                "phone": str(existing.phone),
                            }
                        else:
                            recipient_note = f"Получатель: {recipient_name}, {recipient_phone}."

            delivery_comment = _clean_optional(request.POST.get("delivery_comment"))
            if recipient_note:
                delivery_comment = (recipient_note + " " + (delivery_comment or "")).strip()
            if delivery_type == Delivery.DeliveryTypeChoices.pickup:
                pickup_place = _clean_optional(request.POST.get("pickup_place"))
                if pickup_place:
                    delivery_comment = (
                        (recipient_note + " " + pickup_place).strip()
                        if recipient_note
                        else pickup_place
                    )

            delivery_data = {
                "delivery_type": delivery_type,
                "delivery_cost": _clean_optional(request.POST.get("delivery_cost")) or Decimal("0"),
                "comment": delivery_comment,
                "raw_address": _clean_optional(request.POST.get("delivery_address")),
            }

            payment_data = {
                "payment_method": request.POST.get("payment_method", "cash"),
            }

            order = OrderCreator(
                carts=selected_cart_items,
                order_data=order_data,
                customer_data=customer_data,
                recipient_data=recipient_data,
                delivery_data=delivery_data,
                payment_data=payment_data,
                session_id=request.session.session_key,
            ).create()

            return redirect("market:order_success", order_id=order.id)

        except (ValidationError, OrderDeliveryException, OrderCreatorException, ValueError) as e:
            messages.error(request, f"Ошибка оформления: {e}")
            return redirect("market:cart")
        except Exception as e:
            messages.error(request, f"Ошибка оформления: {e}")
            return redirect("market:cart")

    total_price = Decimal("0.00")
    total_discount = Decimal("0.00")
    final_price = Decimal("0.00")

    for item in cart_items:
        current_price = item.price or item.product.price
        old_price = item.product.old_price or current_price
        total_price += old_price * item.quantity
        final_price += current_price * item.quantity
        if old_price > current_price:
            total_discount += (old_price - current_price) * item.quantity

    return render(
        request,
        "market/checkout.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "total_discount": total_discount,
            "final_price": final_price,
        },
    )


def order_detail_view(request, order_id):
    """Order detail page"""
    order = get_object_or_404(
        Order.objects.select_related("user", "delivery", "payment").prefetch_related(
            "items__product"
        ),
        id=order_id,
        **get_order_item_creator_kwark_by_request(request),
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
    order = get_object_or_404(
        Order.objects.select_related("user", "delivery", "payment"),
        id=order_id,
        **get_order_item_creator_kwark_by_request(request),
    )

    return render(
        request,
        "market/order_success.html",
        {
            "order": order,
        },
    )


@login_required
def account_view(request):
    """User account page with order history"""
    orders = (
        Order.objects.filter(
            **get_order_item_creator_kwark_by_request(request),
        )
        .select_related("delivery", "payment")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "market/account.html",
        {
            "orders": orders,
        },
    )
