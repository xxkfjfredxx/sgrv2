from rest_framework.routers import DefaultRouter
from django.urls import path

# Importa tus ViewSets y la función summary
from apps.empresa.views import CompanyViewSet
from apps.empleados.views import (
    EmployeeViewSet,
    EmployeeDocumentViewSet,
    DocumentTypeViewSet,
)
from apps.auditoria.views import (
    SystemAuditViewSet,
    AuditChecklistViewSet,
    AuditItemViewSet,
    AuditExecutionViewSet,
    AuditResultViewSet,
    AuditFindingViewSet,
)
from apps.usuarios.views import UserViewSet, UserRoleViewSet

router = DefaultRouter()


router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"employees", EmployeeViewSet, basename="employees")  # ✅
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")   
router.register(r"users", UserViewSet)
router.register(r"user-roles", UserRoleViewSet)
router.register(r"documents", EmployeeDocumentViewSet, basename="employee-document")

router.register(r"system-audit", SystemAuditViewSet)
router.register(r"audit-checklists", AuditChecklistViewSet)
router.register(r"audit-items", AuditItemViewSet)
router.register(r"audit-executions", AuditExecutionViewSet)
router.register(r"audit-results", AuditResultViewSet)
router.register(r"audit-findings", AuditFindingViewSet)
# 2) Insertamos summary ANTES de router.urls
urlpatterns = [
    
] + router.urls
