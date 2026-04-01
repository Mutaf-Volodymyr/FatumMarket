import asyncio
import logging
import os

from aiogram.types import BotCommand
from django.core.management.base import BaseCommand

from interfaces.telegram.tg_actions.bot import create_bot, create_dispatcher

logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand(command="start", description="Авторизация"),
    BotCommand(command="settings", description="Управление подписками"),
    BotCommand(command="logout", description="Выйти из аккаунта"),
    BotCommand(command="help", description="Список команд"),
]


class Command(BaseCommand):
    help = "Run Telegram bot polling"

    def handle(self, *args, **options):
        asyncio.run(self._run())

    async def _run(self):
        token = os.getenv("ACTION_TG_BOT_TOKEN")
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://fatum-redis:6379/0")

        if not token:
            raise RuntimeError("ACTION_TG_BOT_TOKEN is not set")

        bot = create_bot(token)
        dp = create_dispatcher(redis_url)

        await bot.set_my_commands(BOT_COMMANDS)

        self.stdout.write("Starting bot polling...")
        await dp.start_polling(bot)
