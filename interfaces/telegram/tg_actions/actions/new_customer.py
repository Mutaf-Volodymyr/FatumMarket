from aiogram import Bot

from interfaces.telegram.tg_actions.actions import dispatch_event
from interfaces.telegram.tg_actions.models import ActionTypes


async def notify_new_customer(bot: Bot, user_id: int) -> None:
    try:
        from asgiref.sync import sync_to_async

        from apps.users.models import User

        user = await sync_to_async(User.objects.get)(pk=user_id)
    except Exception:
        return

    text = _format(user)
    await dispatch_event(bot, ActionTypes.NEW_CUSTOMER, text)


def _format(user) -> str:
    name = " ".join(filter(None, [user.first_name, user.last_name])) or "—"
    lines = [
        "👤 <b>Новый клиент</b>\n",
        f"<b>Имя:</b> {name}",
        f"📞 {user.phone or user.email or '—'}",
    ]
    return "\n".join(lines)
