import asyncio
import logging
import os

import django
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../config/docker/.env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from interfaces.telegram.tg_actions.bot import create_bot, create_dispatcher  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    token = os.getenv("ACTION_TG_BOT_TOKEN")
    redis_url = os.getenv("CELERY_BROKER_URL", "redis://fatum-redis:6379/0")

    if not token:
        raise RuntimeError("ACTION_TG_BOT_TOKEN is not set")

    bot = create_bot(token)
    dp = create_dispatcher(redis_url)

    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
