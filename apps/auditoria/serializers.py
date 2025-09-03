from rest_framework import serializers
from .models import (
    SystemAudit,
    AuditChecklist,
    AuditItem,
    AuditExecution,
    AuditResult,
    AuditFinding,
)


class SystemAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemAudit
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class AuditChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditChecklist
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class AuditItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditItem
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class AuditExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditExecution
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")


class AuditResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditResult
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")