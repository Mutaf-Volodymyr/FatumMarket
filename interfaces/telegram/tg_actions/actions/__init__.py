import logging

from aiogram import Bot

from interfaces.telegram.tg_actions.models import ActionChat

logger = logging.getLogger(__name__)


async def dispatch_event(bot: Bot, action_type: str, text: str) -> None:
    """Send notification to all authorized chats subscribed to action_type."""
    from asgiref.sync import sync_to_async

    chat_ids = await sync_to_async(
        lambda: list(
            ActionChat.objects.filter(
                action_types__contains=[action_type],
                user__isnull=False,
            ).values_list("id", flat=True)
        )
    )()

    if not chat_ids:
        return

    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as exc:
            logger.error("Failed to send to chat %s: %s", chat_id, exc)
