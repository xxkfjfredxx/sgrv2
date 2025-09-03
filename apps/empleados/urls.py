from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.empleados.views import (
    EmployeeViewSet,  # ya existía
    DocumentTypeViewSet,  # ya existía
    EmployeeDocumentViewSet,  # ya existía
    DocumentCategoryViewSet,  # ← NUEVO
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employees")
router.register(r"document-types", DocumentTypeViewSet, basename="document-types")
router.register(r"documents", EmployeeDocumentViewSet, basename="documents")
router.register(
    r"document-categories", DocumentCategoryViewSet, basename="document-categories"
)

urlpatterns = [
    path("", include(router.urls)),
]
