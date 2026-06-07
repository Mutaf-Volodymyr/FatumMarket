from decimal import Decimal

from apps.delivery.models import Delivery
from apps.delivery.shemas import CreateNovaPostaDeliverySchema, CreatePickupDeliverySchema
from apps.orders.schemas import PaymentSchema
from apps.users.domain.schema import UserSchema


def make_new_summary_price_context(cart_items, serializable=False):
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

    if serializable:
        return {
            "total_price": str(total_price),
            "total_discount": str(total_discount),
            "final_price": str(final_price),
            "cart_count": str(cart_items.count()),
        }

    return {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_discount": total_discount,
        "final_price": final_price,
        "cart_count": cart_items.count(),
    }


def get_customer_schema_by_request(request):
    if request.user.is_authenticated:
        return UserSchema(
            id=request.user.id,
            email=request.user.email,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            phone=request.user.phone,
        )
    else:
        customer_name = request.POST.get("customer_name", "") or ""
        customer_name = customer_name.split()
        customer_phone = request.POST.get("customer_phone", "") or ""
        last_name = ""
        first_name = customer_name[0]
        if len(customer_name) == 2:
            last_name = customer_name[1]

        return UserSchema(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=customer_phone.strip(),
            id=None,
            email=None,
        )


def get_recipient_schema_by_request(request):
    recipient_type = request.POST.get("recipient_type", "self")
    if recipient_type == "self":
        return get_customer_schema_by_request(request)
    elif recipient_type == "other":
        recipient_name = request.POST.get("recipient_name", "") or ""
        recipient_name = recipient_name.split()
        recipient_phone = request.POST.get("recipient_phone", "") or ""
        last_name = ""
        first_name = recipient_name[0]
        if len(recipient_name) == 2:
            last_name = recipient_name[1]
        return UserSchema(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=recipient_phone.strip(),
            id=None,
            email=None,
        )
    else:
        raise NotImplementedError("Recipient type '{}' not implemented".format(recipient_type))


def get_delivery_schema_by_request(request):
    from apps.address.schemas import CreateAddressSchema

    delivery_type = request.POST.get("delivery_type")
    if delivery_type == Delivery.DeliveryTypeChoices.PICKUP.value:
        return CreatePickupDeliverySchema(
            comment=request.POST.get("comment", "").strip() or None,
            pickup_place_id=request.POST.get("pickup_place_id"),
        )
    elif delivery_type == Delivery.DeliveryTypeChoices.NOVA_POSTA.value:
        raw_address = request.POST.get("nova_posta_address", "").strip() or None
        return CreateNovaPostaDeliverySchema(
            comment=request.POST.get("comment", "").strip() or None,
            post_office=request.POST.get("post_office") or None,
            parcel_locker=request.POST.get("parcel_locker") or None,
            address=CreateAddressSchema(raw_address=raw_address) if raw_address else None,
        )
    else:
        raise NotImplementedError("Delivery type '{}' not implemented".format(delivery_type))


def get_payment_schema_by_request(request):
    return PaymentSchema(
        payment_method=request.POST.get("payment_method", "cash"),
    )
