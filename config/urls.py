# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views_people import PeopleListView
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)

from config.views_api import urlpatterns as api_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    path("api/", include("apps.usuarios.urls")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("jet/", include("jet.urls", namespace="jet")),
    path("api/people/", PeopleListView.as_view(), name="people-list"),
    path("api/contratistas/", include("apps.contratistas.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api-auth/", include("rest_framework.urls")), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
