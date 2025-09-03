from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.empleados.views import (
    EmployeeViewSet
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employees")

urlpatterns = [
    path("", include(router.urls)),
]
