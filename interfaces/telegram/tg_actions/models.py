from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.users.models import User


class ActionTypes(models.TextChoices):
    NEW_ORDER = "new_order", "Новый заказ"
    NEW_CUSTOMER = "new_customer", "Новый клиент"
    ERRORS = "errors", "Ошибки"


class ActionChat(models.Model):
    id = models.BigIntegerField(primary_key=True)  # Telegram chat_id
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_chats",
        verbose_name="Сотрудник",
    )
    action_types = ArrayField(
        base_field=models.CharField(max_length=50, choices=ActionTypes.choices),
        default=list,
        blank=True,
        verbose_name="Подписки на события",
    )

    @property
    def is_authorized(self) -> bool:
        return self.user_id is not None

    class Meta:
        verbose_name = "Telegram чат"
        verbose_name_plural = "Telegram чаты"

    def __str__(self) -> str:
        return f"Chat {self.id} ({self.user or 'unauthorized'})"
