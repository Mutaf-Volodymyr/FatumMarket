from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from interfaces.telegram.tg_actions.handlers import router


def create_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher(redis_url: str) -> Dispatcher:
    storage = RedisStorage.from_url(redis_url)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    return dp
