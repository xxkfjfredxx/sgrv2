from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django_tenants.utils import tenant_context
from apps.empresa.models import UserCompanyIndex  # public user->company index
from apps.empleados.models import Employee
from apps.usuarios.api.v1.serializers import LoginRequestSerializer, LogoutResponseSerializer, TokenResponseSerializer, UserSerializer
from apps.usuarios.auth import VersionedJWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers as drf_serializers
from django.contrib.auth import logout as dj_logout
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
# =========================
# Vistas
# =========================
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = TokenResponseSerializer

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Email and password are required"),
            401: OpenApiResponse(description="Invalid credentials"),
        },
        tags=["auth"],
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"detail": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # intenta con username=email y con email=email
        user = (
            authenticate(request, username=email, password=password)
            or authenticate(request, email=email, password=password)
        )
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # --- Perfil/empresa exactamente como tenías ---
        if getattr(user, "is_superuser", False):
            user_data = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": True,
            }
            company_id = None
            company_name = None
        else:
            try:
                idx = UserCompanyIndex.objects.get(user=user)
                company = idx.company
            except UserCompanyIndex.DoesNotExist:
                return Response(
                    {"detail": "User has no associated company"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verifica Employee en el schema del tenant
            with tenant_context(company):
                try:
                    Employee.objects.get(user=user)
                except Employee.DoesNotExist:
                    return Response(
                        {"detail": "User has no associated employee"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            company_id = company.id
            company_name = company.name
            user_data = UserSerializer(user).data

        # --- Kill-switch de sesiones: sube la versión ---
        user.token_version = (getattr(user, "token_version", 1) or 1) + 1
        user.save(update_fields=["token_version"])

        # --- Token DRF legacy (compat) ---
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        # --- Inicia sesión de Django (por si usas SessionAuth en admin) ---
        login(request, user)

        # --- JWT firmados con la versión ---
        refresh = RefreshToken.for_user(user)
        refresh["ver"] = user.token_version
        access = refresh.access_token
        access["ver"] = user.token_version

        return Response(
            {
                "token": token.key,               # legacy (puedes retirarlo luego)
                "access": str(access),
                "refresh": str(refresh),
                "user": user_data,
                "company_id": company_id,
                "company_name": company_name,
            },
            status=status.HTTP_200_OK,
        )

class LogoutView(APIView):
    # Permitir sin auth para poder cerrar con solo el refresh (aunque el access ya no sirva)
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        all_sessions = bool(request.data.get("all", False))
        refresh_token = request.data.get("refresh")

        # (A) Cerrar TODAS las sesiones del usuario actual (requiere Authorization válido)
        if all_sessions:
            auth = VersionedJWTAuthentication().authenticate(request)
            if auth:
                user, _ = auth
                # Blacklistea todos los refresh del usuario
                try:
                    for ot in OutstandingToken.objects.filter(user=user):
                        BlacklistedToken.objects.get_or_create(token=ot)
                except Exception:
                    pass
                # ⬅️ Kill-switch: sube la versión para invalidar TODOS los access inmediatamente
                try:
                    user.token_version = (getattr(user, "token_version", 1) or 1) + 1
                    user.save(update_fields=["token_version"])
                except Exception:
                    pass
                # Limpia token DRF legacy
                Token.objects.filter(user_id=user.id).delete()

        # (B) Cerrar UNA sesión por refresh concreto (NO depende de Authorization)
        if refresh_token:
            try:
                rt = RefreshToken(refresh_token)   # valida que sea un refresh válido
                uid = rt.get("user_id", None)
                rt.blacklist()                     # invalida ese refresh
                if uid:
                    # ⬅️ Kill-switch: sube la versión del dueño de ese refresh => mata TODOS los access
                    from apps.usuarios.models import User
                    u = User.objects.filter(pk=uid).first()
                    if u:
                        u.token_version = (getattr(u, "token_version", 1) or 1) + 1
                        u.save(update_fields=["token_version"])
                        Token.objects.filter(user_id=u.id).delete()
            except Exception:
                # refresh inválido o ya blacklisteado -> idempotente, no revientes
                pass

        # (C) Cierra sesión de SessionAuth si hubiera
        try:
            dj_logout(request)
        except Exception:
            pass

        # Idempotente: siempre 204 (sin cuerpo)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(responses=UserSerializer, tags=["auth"])
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
