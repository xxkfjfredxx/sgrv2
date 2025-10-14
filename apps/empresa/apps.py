from django.apps import AppConfig


class EmpresaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.empresa"

    def ready(self):
        # Import signals
        import apps.empresa.signals  # noqa: F401
