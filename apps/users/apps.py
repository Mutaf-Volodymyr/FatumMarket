from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        import interfaces.admin.users  # noqa: F401
        from apps.users import signals  # noqa: F401
