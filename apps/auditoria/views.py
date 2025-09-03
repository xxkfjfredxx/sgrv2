from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_date
from apps.utils.auditlogmimix import AuditLogMixin

from .models import (
    SystemAudit,
    AuditChecklist,
    AuditItem,
    AuditExecution,
    AuditResult,
    AuditFinding,
)
from .serializers import (
    SystemAuditSerializer,
    AuditChecklistSerializer,
    AuditItemSerializer,
    AuditExecutionSerializer,
    AuditResultSerializer,
    AuditFindingSerializer,
)


# --------- READ-ONLY LOGS ------------------------------------------------
class SystemAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemAudit.objects.all()
    serializer_class = SystemAuditSerializer
    permission_classes = [AllowAny]  # cambia a IsAdminUser cuando termines de depurar


# --------- CRUD CON AUDITORÍA -------------------------------------------
class AuditChecklistViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = AuditChecklist.objects.filter(is_deleted=False)
    serializer_class = AuditChecklistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if name := self.request.query_params.get("name"):
            qs = qs.filter(name__icontains=name)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Checklist restaurado."}, status=status.HTTP_200_OK)


class AuditItemViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = AuditItem.objects.filter(is_deleted=False)
    serializer_class = AuditItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if chk := self.request.query_params.get("checklist"):
            qs = qs.filter(checklist_id=chk)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Ítem restaurado."}, status=status.HTTP_200_OK)


class AuditExecutionViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = AuditExecution.objects.filter(is_deleted=False)
    serializer_class = AuditExecutionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if chk := self.request.query_params.get("checklist"):
            qs = qs.filter(checklist_id=chk)
        # ?date=YYYY-MM-DD
        if d := self.request.query_params.get("date"):
            if dt := parse_date(d):
                qs = qs.filter(date=dt)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Ejecución restaurada."}, status=status.HTTP_200_OK)


class AuditResultViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = AuditResult.objects.filter(is_deleted=False)
    serializer_class = AuditResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if exe := self.request.query_params.get("execution"):
            qs = qs.filter(execution_id=exe)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Resultado restaurado."}, status=status.HTTP_200_OK)


class AuditFindingViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = AuditFinding.objects.filter(is_deleted=False)
    serializer_class = AuditFindingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if exe := self.request.query_params.get("execution"):
            qs = qs.filter(execution_id=exe)
        if sev := self.request.query_params.get("severity"):
            qs = qs.filter(severity=sev)
        if status_p := self.request.query_params.get("status"):
            qs = qs.filter(status=status_p)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Hallazgo restaurado."}, status=status.HTTP_200_OK)
