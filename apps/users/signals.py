from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User


@receiver(post_save, sender=User, dispatch_uid="post_save:notify_new_customer")
def notify_new_customer(sender, instance: User, created: bool, **kwargs) -> None:
    if not created or instance.is_staff:
        return

    user_pk = instance.pk
    transaction.on_commit(lambda: _notify(user_pk))


def _notify(user_pk: int) -> None:
    from interfaces.telegram.tg_actions.tasks import task_notify_new_customer

    task_notify_new_customer.delay(user_pk)
