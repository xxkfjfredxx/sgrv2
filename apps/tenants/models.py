from django.db import models
from django_tenants.models import TenantMixin  # Importa TenantMixin

# No importa 'Tenant' aquí, porque ya estás definiendo el modelo Tenant
class Tenant(TenantMixin):  # Hereda de TenantMixin
    name = models.CharField(max_length=255)
    domain_url = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Domain(models.Model):
    # Asegúrate de que la relación con Tenant está bien referenciada
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.domain
