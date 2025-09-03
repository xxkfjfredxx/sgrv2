# apps/empleados/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_tenants.utils import schema_context, get_public_schema_name
from apps.empresa.models import UserCompanyIndex
from .models import Employee

@receiver(post_save, sender=Employee)
def ensure_user_index(sender, instance, **kwargs):
    print(f"[SIGNAL] post_save Employee: user_id={instance.user_id}, company_id={instance.company_id}")
    if not instance.user_id:
        print("  ↳ instance.user_id es None, abortando señal.")
        return
    with schema_context(get_public_schema_name()):
        obj, created = UserCompanyIndex.objects.update_or_create(
            user_id=instance.user_id,
            defaults={"company_id": instance.company_id},
        )
        print(f"  ↳ UserCompanyIndex {'CREADO' if created else 'ACTUALIZADO'} para user {instance.user_id}")

@receiver(post_delete, sender=Employee)
def delete_user_index(sender, instance, **kwargs):
    print(f"[SIGNAL] post_delete Employee: user_id={instance.user_id}")
    with schema_context(get_public_schema_name()):
        deleted, _ = UserCompanyIndex.objects.filter(user_id=instance.user_id).delete()
        print(f"  ↳ UserCompanyIndex eliminado? filas borradas={deleted}")
