from aiogram import Bot

from interfaces.telegram.tg_actions.actions import dispatch_event
from interfaces.telegram.tg_actions.models import ActionTypes

_MAX_TRACEBACK = 3500  # Telegram message limit is 4096


async def notify_error(bot: Bot, path: str, error: str) -> None:
    text = _format(path, error)
    await dispatch_event(bot, ActionTypes.ERRORS, text)


def _format(path: str, error: str) -> str:
    lines = [
        "🔴 <b>Ошибка на сайте</b>\n",
        f"<b>URL:</b> {path}\n",
        f"<pre>{error[:_MAX_TRACEBACK]}</pre>",
    ]
    return "\n".join(lines)
