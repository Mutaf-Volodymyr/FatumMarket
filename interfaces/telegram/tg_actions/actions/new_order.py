from aiogram import Bot

from apps.orders.models import Order
from interfaces.telegram.tg_actions.actions import dispatch_event
from interfaces.telegram.tg_actions.models import ActionTypes

_DELIVERY_LABELS = {
    "pickup": "Самовывоз",
    "courier": "Курьер",
    "nova_posta": "Nova Posta",
}

_PAYMENT_LABELS = {
    "cash": "Наличная",
    "cashless": "Безналичная",
}


async def notify_new_order(bot: Bot, order_id: str) -> None:
    try:
        from asgiref.sync import sync_to_async

        order = await sync_to_async(
            lambda: Order.objects.select_related("user", "delivery__address", "payment")
            .prefetch_related("items")
            .get(pk=order_id)
        )()
    except Order.DoesNotExist:
        return

    text = _format(order)
    await dispatch_event(bot, ActionTypes.NEW_ORDER, text)


def _format(order: Order) -> str:
    lines = [f"🛍 <b>Новый заказ #{order.pk}</b>\n"]

    customer = order.user
    name = " ".join(filter(None, [customer.first_name, customer.last_name])) or "—"
    lines.append(f"👤 <b>Заказчик:</b> {name}")
    lines.append(f"📞 {customer.phone or customer.email or '—'}")

    delivery = getattr(order, "delivery", None)
    if delivery:
        label = _DELIVERY_LABELS.get(delivery.delivery_type, delivery.delivery_type)
        lines.append(f"\n🚚 <b>Доставка:</b> {label}")
        if delivery.address:
            lines.append(f"📍 {delivery.address.raw_address}")
        elif delivery.post_office:
            lines.append(f"📮 Отделение №{delivery.post_office}")
        if delivery.comment:
            lines.append(f"💬 {delivery.comment}")

    payment = getattr(order, "payment", None)
    if payment:
        label = _PAYMENT_LABELS.get(payment.payment_method, payment.payment_method)
        lines.append(f"\n💳 <b>Оплата:</b> {label}")

    lines.append("\n📦 <b>Товары:</b>")
    for item in order.items.all():
        price = item.price or 0
        lines.append(
            f"  • {item.product_name or '—'} × {item.quantity} = {price * item.quantity} ₴"
        )

    lines.append(f"\n💰 <b>Итого:</b> {order.total_price} ₴")
    if order.total_discount:
        lines.append(f"🎁 <b>Скидка:</b> {abs(order.total_discount)} ₴")
    if order.comment:
        lines.append(f"\n📝 {order.comment}")

    return "\n".join(lines)
