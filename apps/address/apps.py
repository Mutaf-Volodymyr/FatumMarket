from django.apps import AppConfig


class AddressConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.address"

    def ready(self):
        import apps.address.signals  # noqa: F401
        import interfaces.admin.addresses  # noqa: F401
