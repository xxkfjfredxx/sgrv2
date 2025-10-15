from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django_tenants.utils import tenant_context

from apps.empresa.models import UserCompanyIndex  # public user->company index
from apps.empleados.models import Employee
from apps.usuarios.api.v1.serializers import LoginRequestSerializer, LogoutResponseSerializer, TokenResponseSerializer, UserSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers as drf_serializers

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

        # intenta con username=email y con email=email (si hay backend que soporte email)
        user = (
            authenticate(request, username=email, password=password)
            or authenticate(request, email=email, password=password)
        )
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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

            # Verifica que tenga Employee en el schema del tenant
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

        # regenerar token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        login(request, user)

        return Response(
            {
                "token": token.key,
                "user": user_data,
                "company_id": company_id,
                "company_name": company_name,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutResponseSerializer

    @extend_schema(
        responses={200: LogoutResponseSerializer},
        tags=["auth"],
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(responses=UserSerializer, tags=["auth"])
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
