from django.apps import AppConfig


class FittingConfig(AppConfig):
    name = "apps.fitting"

    def ready(self):
        from interfaces.admin import fitting  # noqa: F401
