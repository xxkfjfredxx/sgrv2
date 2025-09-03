# apps/empleados/serializers.py
from rest_framework import serializers
from .models import (
    Employee,
    EmployeeDocument,
    DocumentType,
    DocumentCategory,
)
from datetime import date


# ─── Categoría ────────────────────────────────────────────────
class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ("id", "name", "description")


# ─── Tipo de documento ────────────────────────────────────────
class DocumentTypeSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentCategory.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = DocumentType
        fields = (
            "id",
            "code",
            "name",
            "category",
            "category_id",
            "requires_expiration",
            "default_expiry_months",
            "created_at",
            "created_by",
        )
        read_only_fields = ("created_at", "created_by")


# ─── Employee y Document existían ─────────────────────────────
class EmployeeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    course_expirations = serializers.SerializerMethodField()
    exam_expirations = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("created_at", "created_by", "user_email")
        extra_kwargs = {
            "company": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "active_company"):
            print(f"Company assigned in serializer: {request.active_company}")
            validated_data["company"] = request.active_company
        else:
            print("No active company found in serializer!")
        return super().create(validated_data)


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    document_type_name = serializers.CharField(
        source="document_type.name", read_only=True
    )
    employee_name = serializers.CharField(source="employee.first_name", read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")
