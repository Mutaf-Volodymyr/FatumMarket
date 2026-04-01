import os

from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_process_init.connect
def init_worker_bot(**kwargs) -> None:
    from django.conf import settings

    token = getattr(settings, "ACTION_TG_BOT_TOKEN", None)
    if not token:
        return
    from interfaces.telegram.tg_actions.worker_context import setup

    setup(token)


@worker_process_shutdown.connect
def shutdown_worker_bot(**kwargs) -> None:
    from interfaces.telegram.tg_actions.worker_context import get_bot, teardown

    if get_bot() is not None:
        teardown()
