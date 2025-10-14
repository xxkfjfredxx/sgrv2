from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from django_tenants.utils import tenant_context
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
import logging

from apps.empresa.models import Company

try:
    from oauth2_provider.contrib.rest_framework import OAuth2Authentication
except Exception:
    OAuth2Authentication = None

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    # Public endpoints (stay in public schema, no tenant_context)
    EXEMPT_PATHS = (
        "/api/auth/login",
        "/api/auth/otp/request",
        "/api/auth/otp/verify",
        "/api/schema",
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
    )

    # Admin-only endpoints that operate in public schema
    ADMIN_PUBLIC_PATHS = (
        "/api/admin/companies",
        "/api/admin/users",
    )

    def process_request(self, request):
        if not request.path.startswith("/api/"):
            return
        if request.method == "OPTIONS":
            return
        if any(request.path.startswith(p) for p in self.EXEMPT_PATHS):
            return

        user = self._authenticate_request_user(request)
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("User not authenticated")

        if any(request.path.startswith(p) for p in self.ADMIN_PUBLIC_PATHS):
            if not getattr(user, "is_superuser", False):
                raise PermissionDenied("Admin required")
            return  # public schema

        header_company_id = request.headers.get("X-Active-Company")
        user_company_id = getattr(user, "company_id", None)

        if getattr(user, "is_superuser", False):
            if not header_company_id:
                return  # superuser in public
            company_id = self._parse_company_id(header_company_id)
        else:
            if header_company_id:
                header_id = self._parse_company_id(header_company_id)
                if not user_company_id or header_id != user_company_id:
                    raise PermissionDenied("Invalid company for this user")
                company_id = header_id
            else:
                if not user_company_id:
                    raise PermissionDenied("No active company")
                company_id = user_company_id

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise PermissionDenied("Company not found")

        request.tenant = company
        request.active_company = company
        ctx = tenant_context(company)
        request._tenant_context = ctx
        ctx.__enter__()

    def process_exception(self, request, exception):
        if hasattr(request, "_tenant_context"):
            try:
                request._tenant_context.__exit__(type(exception), exception, getattr(exception, "__traceback__", None))
            finally:
                delattr(request, "_tenant_context")
        return None

    def process_response(self, request, response):
        if hasattr(request, "_tenant_context"):
            try:
                request._tenant_context.__exit__(None, None, None)
            finally:
                delattr(request, "_tenant_context")
        return response

    # ---------- helpers ----------
    def _authenticate_request_user(self, request):
        if getattr(request, "user", None) and getattr(request.user, "is_authenticated", False):
            return request.user

        if OAuth2Authentication is not None:
            try:
                pair = OAuth2Authentication().authenticate(request)
                if pair:
                    request.user, request.auth = pair
                    return request.user
            except AuthenticationFailed:
                pass

        try:
            pair = SessionAuthentication().authenticate(request)
            if pair:
                request.user, request.auth = pair
                return request.user
        except AuthenticationFailed:
            pass

        try:
            pair = TokenAuthentication().authenticate(request)
            if pair:
                request.user, request.auth = pair
                return request.user
        except AuthenticationFailed:
            pass

        return getattr(request, "user", None)

    def _parse_company_id(self, raw):
        if not raw or not raw.isdigit():
            raise PermissionDenied("Invalid X-Active-Company")
        return int(raw)
