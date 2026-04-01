from typing import Any

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.address.models import Address
from apps.orders.models import Order


@receiver(post_save, sender=Address, dispatch_uid="post_save:validate_created_address")
def validate_created_address(
    sender: type,
    instance: Order,
    created: bool,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Ставит задачу на новые аддресса
    """
    if not created:
        return

    from apps.address.tasks import validate_and_geocode_address

    transaction.on_commit(lambda: validate_and_geocode_address.delay(address_id=instance.id))
