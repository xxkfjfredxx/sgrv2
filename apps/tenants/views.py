from django.shortcuts import render
from django.http import JsonResponse
from .models import Tenant

def tenant_list(request):
    tenants = Tenant.objects.all()
    data = {"tenants": list(tenants.values("id", "name", "domain"))}
    return JsonResponse(data)

def tenant_detail(request, tenant_id):
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        data = {
            "id": tenant.id,
            "name": tenant.name,
            "domain": tenant.domain,
            "is_active": tenant.is_active,
        }
        return JsonResponse(data)
    except Tenant.DoesNotExist:
        return JsonResponse({"error": "Tenant not found"}, status=404)