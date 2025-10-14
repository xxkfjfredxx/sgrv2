# apps/empleados/serializers.py
from rest_framework import serializers
from ...models import (
    Employee
)
from datetime import date

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


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

    @extend_schema_field(OpenApiTypes.OBJECT)  # o define una ListField con child si ya sabes el shape
    def get_course_expirations(self, obj):
        # TODO: implementa la lógica real si aplica
        return {}

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_exam_expirations(self, obj):
        # TODO: implementa la lógica real si aplica
        return {}

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "active_company"):
            print(f"Company assigned in serializer: {request.active_company}")
            validated_data["company"] = request.active_company
        else:
            print("No active company found in serializer!")
        return super().create(validated_data)
