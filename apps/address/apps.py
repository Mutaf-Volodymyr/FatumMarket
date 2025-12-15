from django.apps import AppConfig


class AddressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.address'
    def ready(self):
        import interfaces.admin.addresses
