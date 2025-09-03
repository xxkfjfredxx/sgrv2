from rest_framework import serializers
from .models import (
    SystemAudit,
    AuditChecklist,
    AuditItem,
    AuditExecution,
    AuditResult,
    AuditFinding,
)
from apps.acciones_correctivas.serializers import ActionItemSerializer


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


class AuditFindingSerializer(serializers.ModelSerializer):
    action_item = ActionItemSerializer(read_only=True)

    class Meta:
        model = AuditFinding
        fields = "__all__"
        read_only_fields = ("created_at", "created_by")
