from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.expedientesdigitales.api.v1.views import (
    DigitalRecordViewSet
)

router = DefaultRouter()
router.register(r"digital-files", DigitalRecordViewSet, basename="digital-files")

urlpatterns = [
    path("", include(router.urls)),
]