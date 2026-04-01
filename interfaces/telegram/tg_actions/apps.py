from django.apps import AppConfig


class TgActionsConfig(AppConfig):
    name = "interfaces.telegram.tg_actions"

    def ready(self):
        from interfaces.telegram.tg_actions import signals  # noqa: F401
