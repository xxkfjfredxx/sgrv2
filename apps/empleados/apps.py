from django.apps import AppConfig


class EmpleadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.empleados"
    def ready(self):
        print("[EmpleadosConfig] ready() llamado: registrando señales de Employee")
        import apps.empleados.signals