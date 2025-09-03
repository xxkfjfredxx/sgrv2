from rest_framework.routers import DefaultRouter
from django.urls import path

# Importa tus ViewSets y la función summary
from apps.empresa.views import CompanyViewSet
from apps.empleados.views import (
    EmployeeViewSet
)
from apps.auditoria.views import (
    SystemAuditViewSet
)
from apps.usuarios.views import UserViewSet, UserRoleViewSet

router = DefaultRouter()


router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"employees", EmployeeViewSet, basename="employees")
router.register(r"users", UserViewSet)
router.register(r"user-roles", UserRoleViewSet)

router.register(r"system-audit", SystemAuditViewSet)
# 2) Insertamos summary ANTES de router.urls
urlpatterns = [
    
] + router.urls
