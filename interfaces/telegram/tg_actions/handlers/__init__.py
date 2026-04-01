from aiogram import Router

from interfaces.telegram.tg_actions.handlers.auth import router as auth_router
from interfaces.telegram.tg_actions.handlers.commands import router as commands_router
from interfaces.telegram.tg_actions.handlers.settings import router as settings_router

router = Router()
router.include_router(commands_router)
router.include_router(auth_router)
router.include_router(settings_router)
