from django.apps import AppConfig


class SupplyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.supply"

    def ready(self):
        import interfaces.admin.supply  # noqa: F401
