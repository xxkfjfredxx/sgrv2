from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_date
from apps.utils.auditlogmimix import AuditLogMixin

from .models import (
    SystemAudit
)
from .serializers import (
    SystemAuditSerializer
)


# --------- READ-ONLY LOGS ------------------------------------------------
class SystemAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemAudit.objects.all()
    serializer_class = SystemAuditSerializer
    permission_classes = [AllowAny]  # cambia a IsAdminUser cuando termines de depurar
