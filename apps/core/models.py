from django.db import models
from django_multitenant.models import TenantModel
from django_multitenant.utils import get_current_tenant
import logging

# Configura el logger
logger = logging.getLogger(__name__)

class TenantBase(TenantModel):
    tenant_id = "company_id"  # Usamos company_id para filtrar entre tenants
    company = models.ForeignKey(
        "empresa.Company",
        on_delete=models.PROTECT,
        help_text="Empresa/tenant al que pertenece este registro",
    )

    def db_for_read(self, model, **hints):
        tenant = get_current_tenant()
        if tenant:
            logger.debug(f"Usando la base de datos para el tenant: {tenant.db_label}")
            return "default"  # Usa la base de datos por defecto para todos los tenants
        logger.debug("No se encontró un tenant. Usando la base de datos por defecto.")
        return "default"  # Usa la base de datos por defecto

    def db_for_write(self, model, **hints):
        tenant = get_current_tenant()
        if tenant:
            logger.debug(f"Escribiendo en la base de datos del tenant: {tenant.db_label}")
            return "default"  # Usa la base de datos por defecto
        logger.debug("No se encontró un tenant. Usando la base de datos por defecto.")
        return "default"  # Usa la base de datos por defecto

    class Meta:
        abstract = True  # No crea tabla propia

    def save(self, *args, **kwargs):
        if not self.company_id:
            self.company = get_current_tenant()
            logger.debug(f"Asignando empresa al registro: {self.company}")
        super().save(*args, **kwargs)
