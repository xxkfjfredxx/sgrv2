# apps/expedientesdigitales/api/v1/serializers.py
from rest_framework import serializers
from apps.categoriadocumentos.models import DocumentCategory
from apps.categoriadocumentos.api.v1.serializers import DocumentCategorySerializer
from ...models import DigitalRecord


class DigitalRecordSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentCategory.objects.all(),
        source="category",
        write_only=True,
    )
    employee_full_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )
    descriptive_name = serializers.CharField(source="nombre_descriptivo")

    class Meta:
        model = DigitalRecord
        fields = [
            "id",
            "employee",
            "employee_full_name",
            "category",
            "category_id",
            "descriptive_name",   # ← ahora mapeado al campo real
            "file",
            "issue_date",
            "expiry_date",
            "created_at",
        ]
        read_only_fields = ["created_at"]
