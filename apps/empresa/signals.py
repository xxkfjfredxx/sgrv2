from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import schema_context, get_public_schema_name

from apps.empresa.models import Company
from apps.usuarios.models import UserRole


DEFAULT_ROLES = (
    {"name": "Admin", "description": "Full access", "access_level": 100},
    {"name": "RRHH", "description": "Human resources", "access_level": 50},
    {"name": "Employee", "description": "Employee self-service", "access_level": 10},
)


@receiver(post_save, sender=Company)
def seed_default_roles_for_company(sender, instance: Company, created: bool, **kwargs):
    """
    When a Company is created (in PUBLIC), ensure default roles exist in PUBLIC for that company.
    Idempotent: uses get_or_create on (company, name).
    """
    if not created:
        return

    # Roles live in PUBLIC schema
    with schema_context(get_public_schema_name()):
        for role in DEFAULT_ROLES:
            UserRole.objects.get_or_create(
                company=instance,
                name=role["name"],
                defaults={
                    "description": role["description"],
                    "access_level": role["access_level"],
                    "is_active": True,
                },
            )
