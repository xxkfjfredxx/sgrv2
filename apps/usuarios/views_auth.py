# apps/usuarios/views_auth.py
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django_tenants.utils import tenant_context
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout

from apps.empresa.models import UserCompanyIndex
from apps.empleados.models import Employee
from apps.usuarios.serializers import UserSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        # 1️⃣ Autenticar en el esquema public
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {"detail": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tenant_id = None
        company_name = None

        # 2️⃣ Superuser → sin tenant
        if user.is_superuser:
            user_data = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": True,
            }

        else:
            # 3️⃣ Usar índice público para resolver la company
            try:
                idx = UserCompanyIndex.objects.get(user=user)
                company = idx.company
            except UserCompanyIndex.DoesNotExist:
                return Response(
                    {"detail": "El usuario no tiene empresa asociada"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4️⃣ Entrar al schema tenant y cargar el Employee
            with tenant_context(company):
                try:
                    employee = Employee.objects.get(user=user)
                except Employee.DoesNotExist:
                    return Response(
                        {"detail": "El usuario no tiene un empleado asociado"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            tenant_id = str(company.id)
            company_name = company.name
            user_data = UserSerializer(user).data

        # 5️⃣ Crear token, iniciar sesión y devolver respuesta
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        login(request, user)

        return Response({
            "token": token.key,
            "user": user_data,
            "tenant_id": tenant_id,
            "company_name": company_name,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /logout/  – Borra token y cierra sesión. Idempotente.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 1️⃣ Elimina el token si existe
        Token.objects.filter(user=request.user).delete()

        # 2️⃣ Cierra la sesión de Django
        logout(request)

        # 3️⃣ Siempre responde 200 OK (idempotencia)
        return Response(
            {"message": "Sesión cerrada correctamente"},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /me/  – Devuelve los datos del usuario autenticado.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
