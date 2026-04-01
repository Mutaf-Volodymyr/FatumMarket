from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from apps.orders.domain.order_creator import OrderCreator, OrderCreatorException
from apps.orders.domain.order_item_card_manager import OrderItemCartManager, OrderItemException
from apps.products.models import Product, Category, Brand
from apps.users.domain.customer_manager import CustomerManager
from apps.users.domain.schema import UserSchema
from apps.users.models import UserStatuses


ALLOWED_STAFF_STATUSES = {
    UserStatuses.MANAGER,
    UserStatuses.SALES_MAN,
    UserStatuses.OWNER,
    UserStatuses.DEVELOPER,
}


def _require_staff_permission(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("auth:login")
        if request.user.staff_status not in ALLOWED_STAFF_STATUSES:
            return HttpResponseForbidden("Недостаточно прав")
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@_require_staff_permission
def staff_create_order_view(request):
    products = Product.objects.filter(is_active=True).select_related("category", "brand").order_by("name")
    categories = Category.objects.all().order_by("name")
    brands = Brand.objects.all().order_by("name")

    if request.method == "POST":
        def _clean(value):
            if value is None:
                return None
            if isinstance(value, str):
                value = value.strip()
                return value or None
            return value

        customer_first_name = _clean(request.POST.get("customer_first_name"))
        customer_last_name = _clean(request.POST.get("customer_last_name"))
        customer_phone = _clean(request.POST.get("customer_phone"))

        if not customer_phone:
            messages.error(request, "Укажите телефон заказчика")
            return redirect("market:staff_create_order")

        customer_schema = UserSchema.model_validate({
            "first_name": customer_first_name,
            "last_name": customer_last_name,
            "phone": customer_phone,
        })
        customer = CustomerManager.get_or_create_customer(customer_schema)
        if customer is None:
            messages.error(request, "Не удалось создать заказчика")
            return redirect("market:staff_create_order")

        recipient_data = {}

        delivery_type = request.POST.get("delivery_type", "pickup")
        raw_address = _clean(request.POST.get("delivery_address"))
        if delivery_type == "courier" and not raw_address:
            messages.error(request, "Для курьерской доставки нужен адрес")
            return redirect("market:staff_create_order")

        delivery_data = {
            "delivery_type": delivery_type,
            "raw_address": raw_address,
            "comment": _clean(request.POST.get("delivery_comment")),
            "delivery_cost": _clean(request.POST.get("delivery_cost")),
        }

        payment_data = {
            "payment_method": request.POST.get("payment_method", "cash"),
        }

        selected_product_ids = request.POST.getlist("product_id")
        if not selected_product_ids:
            messages.error(request, "Выберите товары")
            return redirect("market:staff_create_order")

        cart_items = []
        try:
            for product_id in selected_product_ids:
                qty_value = _clean(request.POST.get(f"quantity_{product_id}")) or "1"
                quantity = int(qty_value)
                if quantity <= 0:
                    continue
                existing = Product.objects.filter(id=product_id, is_active=True).first()
                if existing is None:
                    continue
                existing_cart = customer.orderitem_set.filter(
                    product_id=product_id,
                    status=customer.orderitem_set.model.OrderItemStatus.CARD,
                ).first()
                if existing_cart:
                    manager = OrderItemCartManager(instance=existing_cart)
                    manager.update_quantity(existing_cart.quantity + quantity)
                    cart_items.append(existing_cart)
                else:
                    manager = OrderItemCartManager(data={
                        "user_id": customer.id,
                        "product_id": product_id,
                        "quantity": quantity,
                    })
                    cart_items.append(manager.create_cart())
        except (OrderItemException, ValueError) as exc:
            messages.error(request, f"Ошибка по товарам: {exc}")
            return redirect("market:staff_create_order")

        if not cart_items:
            messages.error(request, "Добавьте хотя бы один товар с количеством")
            return redirect("market:staff_create_order")

        try:
            order = OrderCreator(
                carts=cart_items,
                order_data={"comment": _clean(request.POST.get("order_comment"))},
                customer_data={
                    "first_name": customer_first_name,
                    "last_name": customer_last_name,
                    "phone": customer_phone,
                },
                recipient_data=recipient_data,
                delivery_data=delivery_data,
                payment_data=payment_data,
            ).create()
        except (OrderCreatorException, OrderItemException, ValueError) as exc:
            messages.error(request, f"Ошибка оформления: {exc}")
            return redirect("market:staff_create_order")

        messages.success(request, f"Заказ {order.id} создан")
        return redirect("market:order_success", order_id=order.id)

    return render(request, "market/staff_create_order.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
    })
