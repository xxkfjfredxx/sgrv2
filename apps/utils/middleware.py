from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import PermissionDenied
from apps.empresa.models import Company
from django_tenants.utils import tenant_context


class TenantMiddleware(MiddlewareMixin):
    # Rutas que NO deben pasar por la lógica de tenant/auth estricta
    EXEMPT_PATHS = (
        "/api/schema",               # JSON (con o sin barra final)
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
        "/api-auth/",                # DRF login/logout por sesión
        "/api/login/",
        "/api/logout/",
    )

    def process_request(self, request):
        print("Verificando el middleware: Proceso de asignación de compañía activa")

        # Solo aplica a rutas /api/
        if not request.path.startswith("/api/"):
            return

        # Preflight CORS
        if request.method == "OPTIONS":
            return

        # Excepciones (doc pública, auth por sesión, login/logout)
        if any(request.path.startswith(p) for p in self.EXEMPT_PATHS):
            return

        # --- Autenticación por Token (igual que tu lógica actual) ---
        try:
            user_auth_tuple = TokenAuthentication().authenticate(request)
            if user_auth_tuple is not None:
                request.user, request.auth = user_auth_tuple
        except AuthenticationFailed:
            raise PermissionDenied("Token inválido o expirado")

        # Debe estar autenticado a partir de aquí
        user = getattr(request, "user", None)
        if not getattr(user, "is_authenticated", False):
            raise PermissionDenied("Usuario no autenticado")

        # --- Compañía activa desde header (misma lógica tuya) ---
        company_id = request.headers.get("X-Active-Company")
        if not company_id:
            # Mantener comportamiento tuyo: si no viene header, no se cambia el schema.
            return

        if not company_id.isdigit():
            raise PermissionDenied("X-Active-Company inválido")

        try:
            company = Company.objects.get(pk=int(company_id))
        except Company.DoesNotExist:
            raise PermissionDenied("Compañía no encontrada")

        request.tenant = company
        request._tenant_context = tenant_context(company)
        request._tenant_context.__enter__()
        request.active_company = company

    def process_response(self, request, response):
        if hasattr(request, "_tenant_context"):
            request._tenant_context.__exit__(None, None, None)
        return response
