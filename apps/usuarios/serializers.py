from rest_framework import serializers
from apps.empresa.models import Company
from .models import UserRole, User


# ──────────────────────────────────────────────────────────────
# 1.  ROLE
# ──────────────────────────────────────────────────────────────
class UserRoleSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = UserRole
        fields = ["id", "name", "description", "company", "permissions", "access_level", "is_deleted"]
        read_only_fields = ("created_at", "created_by")


# ──────────────────────────────────────────────────────────────
# 2.  USER
# ──────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        source="role",
        write_only=True,
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        required=False,       # si falta lo tomamos del rol
    )
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
            'is_deleted',
            "is_active",
        ]
        extra_kwargs = {
            "username": {"validators": []}, 
            "password": {"write_only": True, "required": True},
        }

    # ---------- helpers ----------
    def get_employee_id(self, obj):
        if obj.is_superuser:
            return None
        try:
            return obj.employee.id
        except Exception:
            return None


    # ---------- create ----------
    def create(self, validated_data):
        password   = validated_data.pop("password")
        role_obj   = validated_data.get("role")
        company_obj = validated_data.get("company")     # ← ya NO se hace pop

        if company_obj is None and role_obj:
            company_obj = role_obj.company

        if company_obj is None:
            raise serializers.ValidationError(
                {"company": "Obligatorio para usuarios normales."}
            )

        # garantizamos que la clave exista antes del INSERT
        validated_data["company"] = company_obj

        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    # ---------- update ----------
    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data.pop("password"))

        # si viene company es un objeto; Django lo maneja sin problema
        return super().update(instance, validated_data)

    # ---------- validación cruzada ----------
    def validate(self, data):
        is_super = data.get("is_superuser", False)
        company  = data.get("company") or getattr(self.instance, "company", None)
        role     = data.get("role")    or getattr(self.instance, "role", None)

        if not is_super and company is None:
            raise serializers.ValidationError(
                {"company": "Obligatorio para usuarios normales."})
        if not is_super and role is None:
            raise serializers.ValidationError(
                {"role_id": "Obligatorio para usuarios normales."})
        return data

    def validate_username(self, username):
        company = self.initial_data.get("company")

        if not company:
            # Ya lo manejas como obligatorio más abajo en validate()
            return username

        # Verifica si ya existe ese username en esa misma empresa
        user_qs = User.objects.filter(username=username, company_id=company)
        if self.instance:
            user_qs = user_qs.exclude(id=self.instance.id)
        if user_qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese username en esta empresa.")
        return username
