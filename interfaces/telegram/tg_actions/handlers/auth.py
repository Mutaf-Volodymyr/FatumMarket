from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate

from apps.users.models import UserStatuses
from interfaces.telegram.tg_actions.models import ActionChat
from interfaces.telegram.tg_actions.states import AuthStates

router = Router()

ALLOWED_STATUSES = {
    UserStatuses.OWNER,
    UserStatuses.DEVELOPER,
    UserStatuses.MANAGER,
    UserStatuses.SALES_MAN,
}


@router.message(AuthStates.waiting_login)
async def process_login(message: Message, state: FSMContext) -> None:
    await state.update_data(login=message.text.strip())
    await state.set_state(AuthStates.waiting_password)
    await message.answer("Введите пароль:")


@router.message(AuthStates.waiting_password)
async def process_password(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    login = data.get("login", "")
    password = message.text.strip()

    await state.clear()
    await message.delete()

    user = await sync_to_async(authenticate)(username=login, password=password)

    if user is None or not user.is_active:
        await message.answer("❌ Неверный логин или пароль. Попробуйте /start снова.")
        return

    if user.staff_status not in ALLOWED_STATUSES:
        await message.answer("❌ Недостаточно прав для доступа к боту.")
        return

    chat_id = message.chat.id

    await sync_to_async(_save_chat)(chat_id, user.pk)

    await message.answer(
        f"✅ Авторизован как <b>{user.first_name or user.username}</b>!\n\n"
        "Используй /settings для управления подписками на события."
    )


def _save_chat(chat_id: int, user_id) -> None:
    ActionChat.objects.update_or_create(
        id=chat_id,
        defaults={"user_id": user_id},
    )
