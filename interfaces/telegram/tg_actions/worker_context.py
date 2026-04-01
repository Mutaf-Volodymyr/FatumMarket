"""
Bot singleton for Celery workers.

One bot instance + one event loop per worker process.
The loop runs forever in a background daemon thread.
Tasks submit coroutines via run_async() and block until done.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Coroutine, Optional

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

_bot: Optional[Bot] = None
_loop: Optional[asyncio.AbstractEventLoop] = None
_thread: Optional[threading.Thread] = None


def setup(token: str) -> None:
    global _bot, _loop, _thread

    _loop = asyncio.new_event_loop()
    _bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    _thread = threading.Thread(target=_run_loop, args=(_loop,), daemon=True, name="celery-tg-loop")
    _thread.start()

    logger.info("Telegram bot initialized for worker process (pid=%s)", _get_pid())


def teardown() -> None:
    global _bot, _loop, _thread

    if _bot and _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(_bot.session.close(), _loop).result(timeout=10)

    if _loop and _loop.is_running():
        _loop.call_soon_threadsafe(_loop.stop)

    if _thread:
        _thread.join(timeout=5)

    _bot = None
    _loop = None
    _thread = None
    logger.info("Telegram bot shutdown complete")


def get_bot() -> Optional[Bot]:
    return _bot


def run_async(coro: Coroutine) -> Any:
    """Submit coroutine to the worker's event loop and wait for result."""
    if _loop is None or not _loop.is_running():
        raise RuntimeError("Worker event loop is not running. Bot not initialized.")
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result()


def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _get_pid() -> int:
    import os

    return os.getpid()
