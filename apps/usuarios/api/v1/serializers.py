from rest_framework import serializers
from apps.empresa.models import Company
from ...models import UserRole, User
from typing import Optional
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class UserRoleSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), write_only=True, required=True)

    class Meta:
        model = UserRole
        fields = ["id", "name", "description", "company", "permissions", "access_level", "is_deleted"]
        read_only_fields = ("created_at", "created_by")


class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all(), source="role", write_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)
    employee_id = serializers.SerializerMethodField()
    is_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model  = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "is_superuser", "is_staff",
            "role", "role_id",
            "company",
            "employee_id",
            "password",
            "is_deleted",
            "is_active",
        ]
        extra_kwargs = {
            "username": {"validators": []},
            "password": {"write_only": True, "required": True},
        }

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_employee_id(self, obj) -> Optional[int]:
        if obj.is_superuser:
            return None
        try:
            return obj.employee.id
        except Exception:
            return None

    def create(self, validated_data):
        password     = validated_data.pop("password")
        role_obj     = validated_data.get("role")
        company_obj  = validated_data.get("company")

        if company_obj is None and role_obj:
            company_obj = role_obj.company
        if company_obj is None and not validated_data.get("is_superuser", False):
            raise serializers.ValidationError({"company": "Required for non-superusers."})
        if role_obj and company_obj and role_obj.company_id != company_obj.id:
            raise serializers.ValidationError({"role_id": "Role does not belong to the same company."})

        validated_data["company"] = company_obj
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))
        role_obj    = validated_data.get("role", instance.role)
        company_obj = validated_data.get("company", instance.company)
        if role_obj and company_obj and role_obj.company_id != company_obj.id:
            raise serializers.ValidationError({"role_id": "Role does not belong to the same company."})
        return super().update(instance, validated_data)

    def validate(self, data):
        is_super = data.get("is_superuser", getattr(self.instance, "is_superuser", False))
        company  = data.get("company") or getattr(self.instance, "company", None)
        role     = data.get("role")    or getattr(self.instance, "role", None)

        if not is_super and company is None:
            raise serializers.ValidationError({"company": "Required for non-superusers."})
        if not is_super and role is None:
            raise serializers.ValidationError({"role_id": "Required for non-superusers."})
        if role and company and role.company_id != getattr(company, "id", None):
            raise serializers.ValidationError({"role_id": "Role does not belong to the same company."})
        return data

    def validate_username(self, username):
        company = self.initial_data.get("company")
        if not company:
            return username
        qs = User.objects.filter(username=username, company_id=company)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Username already exists for this company.")
        return username

# Serializador para la autenticación de login (Request)
class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# Respuesta del login (con token y datos del usuario)
class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField(required=False, allow_blank=True)
    refresh = serializers.CharField(required=False, allow_blank=True)
    token = serializers.CharField()
    user = UserSerializer()  # Usuario detallado usando su serializer
    company_id = serializers.IntegerField(allow_null=True)
    company_name = serializers.CharField(allow_null=True, allow_blank=True)


# Serializador para solicitud OTP (email)
class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


# Respuesta de la solicitud OTP
class OTPRequestResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    dev_code = serializers.CharField(required=False)  # Solo en Debug


# Serializador para verificar el OTP (con código)
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Logged out successfully")