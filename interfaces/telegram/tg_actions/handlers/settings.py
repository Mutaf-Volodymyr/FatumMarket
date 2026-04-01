from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from interfaces.telegram.tg_actions.keyboards import settings_keyboard
from interfaces.telegram.tg_actions.models import ActionChat, ActionTypes

router = Router()


def _get_chat(chat_id: int):
    return ActionChat.objects.filter(pk=chat_id).first()


def _toggle(chat_id: int, action_type: str) -> tuple[ActionChat, bool]:
    chat = ActionChat.objects.get(pk=chat_id)
    types = list(chat.action_types or [])
    if action_type in types:
        types.remove(action_type)
        subscribed = False
    else:
        types.append(action_type)
        subscribed = True
    chat.action_types = types
    chat.save(update_fields=["action_types"])
    return chat, subscribed


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    chat = await sync_to_async(_get_chat)(message.chat.id)

    if not chat or not chat.is_authorized:
        await message.answer("❌ Сначала авторизуйтесь через /start.")
        return

    await message.answer(
        "⚙️ <b>Настройки подписок</b>\n\nВыберите события для получения уведомлений:",
        reply_markup=settings_keyboard(set(chat.action_types or [])),
    )


@router.callback_query(F.data.startswith("toggle:"))
async def toggle_subscription(callback: CallbackQuery) -> None:
    action_type = callback.data.split(":", 1)[1]

    if action_type not in ActionTypes.values:
        await callback.answer("Неизвестный тип события.")
        return

    chat = await sync_to_async(_get_chat)(callback.message.chat.id)
    if not chat or not chat.is_authorized:
        await callback.answer("❌ Сначала авторизуйтесь.")
        return

    chat, subscribed = await sync_to_async(_toggle)(callback.message.chat.id, action_type)
    label = "подписались на" if subscribed else "отписались от"

    await callback.message.edit_reply_markup(
        reply_markup=settings_keyboard(set(chat.action_types or []))
    )
    await callback.answer(f"Вы {label}: {ActionTypes(action_type).label}")
