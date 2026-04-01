import logging

from config.celery import app

logger = logging.getLogger(__name__)


def _get_bot():
    from interfaces.telegram.tg_actions.worker_context import get_bot

    return get_bot()


def _run(coro):
    from interfaces.telegram.tg_actions.worker_context import run_async

    run_async(coro)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def task_notify_new_order(self, order_id: str) -> None:
    from interfaces.telegram.tg_actions.actions.new_order import notify_new_order

    bot = _get_bot()
    if bot is None:
        logger.warning("Bot not initialized, skipping notification for order %s", order_id)
        return

    try:
        _run(notify_new_order(bot, order_id))
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def task_notify_new_customer(self, user_id: int) -> None:
    from interfaces.telegram.tg_actions.actions.new_customer import notify_new_customer

    bot = _get_bot()
    if bot is None:
        logger.warning("Bot not initialized, skipping notification for user %s", user_id)
        return

    try:
        _run(notify_new_customer(bot, user_id))
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=2, default_retry_delay=30)
def task_notify_error(self, path: str, error: str) -> None:
    from interfaces.telegram.tg_actions.actions.errors import notify_error

    bot = _get_bot()
    if bot is None:
        return

    try:
        _run(notify_error(bot, path, error))
    except Exception as exc:
        raise self.retry(exc=exc)
