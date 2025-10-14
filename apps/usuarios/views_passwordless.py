from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.conf import settings
from rest_framework.authtoken.models import Token
import secrets
from datetime import timedelta

from apps.usuarios.models import User, LoginOTP
from django_tenants.utils import tenant_context

from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from apps.usuarios.api.v1.serializers import OTPRequestSerializer, OTPRequestResponseSerializer, OTPVerifySerializer,TokenResponseSerializer


def _issue_otp_for_user(user):
    code = f"{secrets.randbelow(10**6):06d}"
    otp = LoginOTP.objects.create(
        user=user,
        code_hash=LoginOTP.hash_code(code),
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    return code, otp


class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        request=OTPRequestSerializer,
        responses={200: OTPRequestResponseSerializer},
        tags=["auth"]
    )
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email, is_active=True).first()
        # Return 200 either way (do not reveal existence)
        if user:
            code, _ = _issue_otp_for_user(user)
            # TODO: send code via email; in DEBUG return code for testing
            if settings.DEBUG:
                return Response({"status": "ok", "dev_code": code}, status=status.HTTP_200_OK)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Invalid or expired code"),
        },
        tags=["auth"]
    )
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        code = (request.data.get("code") or "").strip()

        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        code_hash = LoginOTP.hash_code(code)
        otp = LoginOTP.objects.filter(user=user, code_hash=code_hash).order_by("-created_at").first()
        if not otp or otp.is_expired():
            return Response({"detail": "Invalid or expired code"}, status=status.HTTP_400_BAD_REQUEST)

        otp.delete()

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        company_id = getattr(user, "company_id", None)
        company_name = getattr(getattr(user, "company", None), "name", None)

        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": bool(user.is_superuser),
                "role": getattr(getattr(user, "role", None), "name", None),
            },
            "company_id": company_id,
            "company_name": company_name,
        }, status=status.HTTP_200_OK)


# añade estos serializers (debajo de imports)
class OTPRequestSerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField()

class OTPRequestResponseSerializer(drf_serializers.Serializer):
    status = drf_serializers.CharField()
    # solo en DEBUG devolvemos dev_code; lo dejamos opcional en schema
    dev_code = drf_serializers.CharField(required=False)

class OTPVerifySerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField()
    code = drf_serializers.CharField()
