from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.models import Order, OrderItem
from apps.products.models import Product


@receiver(post_save, sender=Order, dispatch_uid="post_save:create_order_logic")
def create_order_logic(
    sender: type,
    instance: Order,
    created: bool,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Заполняет данные в OrderItem о цене, скидке, имени товара на момент покупки.

    Переводит OrderItem.status в ORDER

    Обновляет Product.quantity в изоляции
    """
    if not created:
        return

    items = []
    products = []

    items_qs = instance.items.select_related('product')

    # Изоляция продуктов
    products_qs = Product.objects.filter(
        id__in=[item.product_id for item in items]
    ).select_for_update()

    for item in items_qs:

        # OrderItem
        item.price = item.product.price
        item.discount = item.product.discount
        item.product_name = item.product.name
        item.status = item.OrderItemStatus.ORDER

        items.append(item)

        # Product
        if item.product.quantity < item.quantity:
            raise ValidationError(
                    "Недостаточное количество товара %s в наличии\n"
                        "Доступно: %s", item.product.name, item.product.quantity
                )
        item.product.quantity -= item.quantity

        products.append(item.product)

    # Обновление
    OrderItem.objects.bulk_update(
        items, fields=['price', 'discount', 'product_name', 'status']
    )
    Product.objects.bulk_update(
        products, fields=['quantity']
    )
