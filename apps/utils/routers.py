# apps/utils/routers.py

from django_multitenant.utils import get_current_tenant

class TenantRouter:
    """
    Dirige lecturas y escrituras a la base de datos correspondiente
    según el tenant activo (Company.db_label), o usa 'default'.
    """

    def db_for_read(self, model, **hints):
        tenant = get_current_tenant()
        # Verifica que el tenant esté presente
        if tenant:
            return getattr(tenant, "db_label", "default")
        return "default"

    def db_for_write(self, model, **hints):
        tenant = get_current_tenant()
        # Verifica que el tenant esté presente
        if tenant:
            return getattr(tenant, "db_label", "default")
        return "default"
