import sys
import traceback

from django.core.signals import got_request_exception
from django.dispatch import receiver


@receiver(got_request_exception, dispatch_uid="tg_actions:got_request_exception")
def on_request_exception(sender, request, **kwargs) -> None:
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_value is None:
        return

    path = getattr(request, "path", "unknown")
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

    from interfaces.telegram.tg_actions.tasks import task_notify_error

    task_notify_error.delay(path, error_text)
