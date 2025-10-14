from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentCategoryViewSet
)

router = DefaultRouter()
#los tipos de documentos como salud,documento identidad,titulos etc
router.register(r"document-categories-types", DocumentCategoryViewSet, basename="document-categories-types")

urlpatterns = [
    path("", include(router.urls)),
]
