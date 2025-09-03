from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemAuditViewSet,
    AuditChecklistViewSet,
    AuditItemViewSet,
    AuditExecutionViewSet,
    AuditResultViewSet,
    AuditFindingViewSet,
)

router = DefaultRouter()
router.register(r"system-audit", SystemAuditViewSet, basename="system-audit")
router.register(r"audit-checklists", AuditChecklistViewSet, basename="audit-checklists")
router.register(r"audit-items", AuditItemViewSet, basename="udit-items")
router.register(r"audit-executions", AuditExecutionViewSet, basename="audit-executions")
router.register(r"audit-results", AuditResultViewSet, basename="audit-results")
router.register(r"audit-findings", AuditFindingViewSet, basename="udit-findings")

urlpatterns = [
    path("", include(router.urls)),
]
