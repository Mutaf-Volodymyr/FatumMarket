from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from interfaces.telegram.tg_actions.models import ActionTypes


def settings_keyboard(subscribed: set[str]) -> InlineKeyboardMarkup:
    buttons = []
    for value, label in ActionTypes.choices:
        icon = "✅" if value in subscribed else "⬜"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {label}",
                    callback_data=f"toggle:{value}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
