from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from interfaces.telegram.tg_actions.models import ActionChat
from interfaces.telegram.tg_actions.states import AuthStates

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    chat_id = message.chat.id

    chat, _ = await sync_to_async(
        lambda: ActionChat.objects.select_related("user").get_or_create(id=chat_id)
    )()

    if chat.is_authorized:
        await message.answer(
            f"👋 С возвращением, <b>{chat.user.first_name or chat.user.username}</b>!\n\n"
            "Используй /settings для управления подписками."
        )
        return

    await state.set_state(AuthStates.waiting_login)
    await message.answer(
        "👋 <b>FatumMarket Bot</b>\n\n"
        "Для использования бота необходимо авторизоваться.\n\n"
        "Введите ваш логин (телефон или email):"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Доступные команды:</b>\n\n"
        "/start — авторизация\n"
        "/settings — управление подписками\n"
        "/logout — выйти из аккаунта\n"
        "/help — список команд"
    )


@router.message(Command("logout"))
async def cmd_logout(message: Message) -> None:
    chat_id = message.chat.id

    updated = await sync_to_async(lambda: ActionChat.objects.filter(pk=chat_id).update(user=None))()

    if updated:
        await message.answer("✅ Вы вышли из аккаунта.")
    else:
        await message.answer("Вы не были авторизованы.")
