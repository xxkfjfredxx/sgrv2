from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from django.db.models import Q
from django_tenants.utils import tenant_context

from ...models import User, UserRole
from .serializers import UserSerializer, UserRoleSerializer
from ...permissions import EsRolPermitido  # keep your existing permission name
from apps.utils.auditlogmimix import AuditLogMixin
from apps.empleados.models import Employee


class UserRoleViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = UserRole.objects.filter(is_deleted=False)
    serializer_class = UserRoleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    roles_permitidos = ["Admin"]        # permission class uses this
    permission_classes = [EsRolPermitido]

    def create(self, request, *args, **kwargs):
        company_id = request.data.get("company")
        name = request.data.get("name")

        if not company_id:
            raise ValidationError({"company": "This field is required."})
        if not name:
            raise ValidationError({"name": "This field is required."})

        user = request.user
        if not user.is_superuser:
            active_company = getattr(request, "active_company", None)
            if not active_company or active_company.id != int(company_id):
                raise PermissionDenied("You don't have permission to create roles in this company.")

        existing = UserRole.objects.filter(company_id=company_id, name=name, is_deleted=True).first()
        if existing:
            existing.is_deleted = False
            existing.description = request.data.get("description", existing.description)
            existing.access_level = request.data.get("access_level", existing.access_level)
            permissions = request.data.get("permissions")
            if permissions is not None:
                existing.permissions = permissions
            existing.save()
            self.log_audit("RESTORED", existing)
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=200)

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        active_company = getattr(self.request, "active_company", None)
        company_id = self.request.query_params.get("company")

        if active_company:
            return qs.filter(company_id=active_company.id)
        if user.is_superuser and company_id:
            return qs.filter(company_id=company_id)
        return qs.none() if not user.is_superuser else qs


class UserViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email"]
    permission_classes = [EsRolPermitido]
    roles_permitidos = ["Admin", "RRHH"]

    def get_object(self):
        if self.action in ["restore_soft", "destroy_hard", "retrieve"]:
            try:
                return User.objects.get(pk=self.kwargs["pk"])
            except User.DoesNotExist:
                raise NotFound("User not found.")
        return super().get_object()

    @action(detail=True, methods=['post'], url_path='restore')
    def restore_soft(self, request, pk=None):
        user = self.get_object()
        user.is_deleted = False
        user.is_active = True
        user.save()
        return Response({'status': 'user restored'})

    @action(detail=True, methods=['delete'], url_path='destroy-hard')
    def destroy_hard(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({'status': 'user permanently deleted'})

    def get_queryset(self):
        user = self.request.user
        include_deleted = self.request.query_params.get("include_deleted") == "true"
        company_param = self.request.query_params.get("company")
        active_company = getattr(self.request, "active_company", None)

        if not user.is_authenticated:
            raise PermissionDenied("Not authenticated.")

        qs = User.objects.all() if include_deleted else User.objects.filter(is_deleted=False)

        if active_company:
            return qs.filter(
                Q(employee__company_id=active_company.id) | Q(role__company_id=active_company.id)
            ).distinct()

        if user.is_superuser and company_param:
            return qs.filter(
                Q(employee__company_id=company_param) | Q(role__company_id=company_param)
            ).distinct()

        return qs if user.is_superuser else User.objects.none()

    def perform_create(self, serializer):
        requester = self.request.user
        active_company = getattr(self.request, "active_company", None)

        if not requester.is_superuser:
            if not active_company:
                raise PermissionDenied("Active company not found.")
            user = serializer.save(company=active_company)
        else:
            user = serializer.save()

        if not user.is_superuser:
            company = user.company
            if not company:
                raise PermissionDenied("User without associated company.")
            with tenant_context(company):
                Employee.objects.create(
                    user=user,
                    company=company,
                    document=str(user.id).zfill(8),
                    first_name=user.first_name or "",
                    last_name=user.last_name or "",
                )
        return user
