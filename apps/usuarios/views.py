from rest_framework import viewsets, filters, status
from .models import User, UserRole
from .serializers import UserSerializer, UserRoleSerializer
from .permissions import EsRolPermitido
from apps.utils.auditlogmimix import AuditLogMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.exceptions import NotFound
from apps.empleados.models import Employee
from django_tenants.utils import tenant_context


class UserRoleViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = UserRole.objects.filter(is_deleted=False)
    serializer_class = UserRoleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    roles_permitidos = ["Admin"]
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
            if not user.role or user.role.company_id != int(company_id):
                raise PermissionDenied("You don't have permission to create roles in this company.")

        # Buscar rol eliminado
        existing = UserRole.objects.filter(
            company_id=company_id,
            name=name,
            is_deleted=True
        ).first()

        if existing:
            # Restaurar
            existing.is_deleted = False
            existing.description = request.data.get("description", existing.description)
            existing.access_level = request.data.get("access_level", existing.access_level)
            existing.save()

            # Actualizar permisos si se enviaron
            permissions = request.data.get("permissions")
            if permissions is not None:
                existing.permissions = permissions
                existing.save()


            # Registrar auditoría
            self.log_audit("RESTORED", existing)

            # Serializar y responder como si fuera nuevo
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=200)

        # Si no existe, crear normalmente
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        company_id = self.request.query_params.get("empresa")
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs


from rest_framework.exceptions import PermissionDenied

class UserViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email"]
    permission_classes = [EsRolPermitido]
    roles_permitidos = ["Admin", "RRHH"]

    def get_object(self):
        # Para acciones que necesitan acceder incluso si el usuario está eliminado
        if self.action in ["restaurar", "eliminar_definitivamente", "retrieve"]:
            try:
                return User.objects.get(pk=self.kwargs["pk"])
            except User.DoesNotExist:
                raise NotFound("Usuario no encontrado.")
        return super().get_object()

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        user = self.get_object()
        user.is_deleted = False
        user.is_active = True
        user.save()
        return Response({'status': 'usuario restaurado'})

    @action(detail=True, methods=['delete'], url_path='eliminar-definitivamente')
    def eliminar_definitivamente(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response({'status': 'usuario eliminado de forma permanente'})

    def get_queryset(self):
        user = self.request.user
        empresa_id = self.request.query_params.get("empresa")
        incluir_eliminados = self.request.query_params.get("incluir_eliminados") == "true"
        active_company = getattr(self.request, "active_company", None)

        if not user.is_authenticated:
            raise PermissionDenied("No estás autenticado.")
        if not active_company:
            raise PermissionDenied("No se encontró la empresa activa.")
        if not user.is_superuser and getattr(user, "company_id", None) != active_company.pk:
            raise PermissionDenied("No tienes permiso para acceder a esta empresa.")

        qs = User.objects.all() if incluir_eliminados else User.objects.filter(is_deleted=False)
        if empresa_id:
            qs = qs.filter(
                Q(employee__company_id=empresa_id) | Q(role__company_id=empresa_id)
            ).distinct()
        return qs

    def perform_create(self, serializer):
        user = serializer.save()
        if not user.is_superuser:
            company = getattr(self.request, "active_company", None)
            if company:
                with tenant_context(company):
                    emp = Employee.objects.create(
                        user=user,
                        company=company,
                        document=str(user.id).zfill(8),
                        first_name=user.first_name or "",
                        last_name=user.last_name or "",
                    )
        return user

class BaseAuditViewSet(AuditLogMixin, viewsets.ModelViewSet):
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        self.log_audit("RESTORED", obj)
        return Response({"detail": "Registro restaurado."}, status=status.HTTP_200_OK)
