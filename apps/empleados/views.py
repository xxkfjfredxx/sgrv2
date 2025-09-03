# apps/empleados/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db import models
from django.core.exceptions import PermissionDenied

from apps.utils.auditlogmimix import AuditLogMixin

from .models import Employee, DocumentType, EmployeeDocument, DocumentCategory
from .serializers import (
    EmployeeSerializer,
    DocumentTypeSerializer,
    EmployeeDocumentSerializer,
    DocumentCategorySerializer,
)


class BaseAuditViewSet(AuditLogMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Registro restaurado."}, status=status.HTTP_200_OK)


class EmployeeViewSet(BaseAuditViewSet):
    serializer_class = EmployeeSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name", "document", "user__email", "phone_contact"]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if not hasattr(self.request, "active_company") or self.request.active_company is None:
            raise PermissionDenied("No se encontró la compañía activa en la solicitud")
        ctx["request"] = self.request
        ctx["active_company"] = self.request.active_company
        return ctx

    def get_queryset(self):
        # Base: siempre cerrar por la empresa activa (multitenant)
        if not hasattr(self.request, "active_company") or self.request.active_company is None:
            raise PermissionDenied("No se encontró la compañía activa en la solicitud")
        active_company = self.request.active_company

        qs = Employee.objects.filter(is_deleted=False)

        # 1) Cierre por compañía activa (si tu modelo Employee tiene FK company)
        qs = qs.filter(company=active_company)

        # 2) Compatibilidad con tu filtro original por EmploymentLink, PERO sin abrir datos de otras compañías.
        #    Si viene ?company=..., solo lo respetamos si coincide con la activa o si el usuario es superuser.
        company_param = self.request.query_params.get("company")
        
        # 3) Filtros por nombre/documento (tus originales)
        if name := self.request.query_params.get("name"):
            qs = qs.filter(models.Q(first_name__icontains=name) | models.Q(last_name__icontains=name))

        if doc := self.request.query_params.get("document"):
            qs = qs.filter(document__icontains=doc)

        return qs.distinct()


class EmployeeDocumentViewSet(BaseAuditViewSet):
    serializer_class = EmployeeDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if not hasattr(self.request, "active_company") or self.request.active_company is None:
            raise PermissionDenied("No se encontró la compañía activa en la solicitud")

        qs = EmployeeDocument.objects.filter(
            is_deleted=False,
            employee__company=self.request.active_company
        )

        if emp := self.request.query_params.get("employee"):
            qs = qs.filter(employee_id=emp)

        if dtype := self.request.query_params.get("document_type"):
            qs = qs.filter(document_type_id=dtype)

        # Si quieres seguir aceptando ?company=... aquí también, aplica la misma regla de seguridad:
        # company_param = self.request.query_params.get("company")
        # if company_param and (str(company_param) == str(self.request.active_company.id) or self.request.user.is_superuser):
        #     qs = qs.filter(company_id=company_param)

        return qs


class DocumentCategoryViewSet(BaseAuditViewSet):
    queryset = DocumentCategory.objects.filter(is_deleted=False)
    serializer_class = DocumentCategorySerializer
    http_method_names = ["get", "head", "options"]


class DocumentTypeViewSet(BaseAuditViewSet):
    serializer_class = DocumentTypeSerializer
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        qs = DocumentType.objects.filter(is_deleted=False)
        if cat := self.request.query_params.get("category"):
            qs = qs.filter(category_id=cat)
        return qs
