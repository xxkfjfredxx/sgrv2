# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)
from .urls_v1 import urlpatterns as api_urls
# 👇 importa tus vistas de auth
from apps.usuarios.api.v1.views_auth import LoginView, LogoutView, MeView
from apps.usuarios.views_passwordless import RequestOTPView, VerifyOTPView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_urls)),

    # Auth (public)
    path("api/auth/login", LoginView.as_view(), name="auth-login"),
    path("api/auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/me", MeView.as_view(), name="auth-me"),
    path("api/auth/refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("api/auth/otp/request", RequestOTPView.as_view(), name="auth-otp-request"),
    path("api/auth/otp/verify", VerifyOTPView.as_view(), name="auth-otp-verify"),

    # --- Docs ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api-auth/", include("rest_framework.urls")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("jet/", include("jet.urls", namespace="jet")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

