from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django_tenants.utils import schema_context
from apps.utils.auditlogmimix import AuditLogMixin
from ...models import Employee
from .serializers import EmployeeSerializer
from apps.usuarios.models import User, UserRole


class EmployeeViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("user", "company").all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["company", "user"]
    search_fields = ["first_name", "last_name", "document"]

    def get_queryset(self):
        qs = super().get_queryset()
        active_company = getattr(self.request, "active_company", None)
        if not active_company:
            raise PermissionDenied("Active company not found.")
        return qs.filter(company_id=active_company.id)

    def perform_create(self, serializer):
        active_company = getattr(self.request, "active_company", None)
        if not active_company:
            raise PermissionDenied("Active company not found.")

        # Asegura que venga email en el payload del empleado
        email = serializer.validated_data.get("email")
        if not email:
            raise ValidationError({"email": "This field is required."})

        # 1) Garantiza que exista un rol 'Employee' en PUBLIC para esta company
        with schema_context("public"):
            role_employee, _ = UserRole.objects.get_or_create(
                company=active_company,
                name="Employee",
                defaults={"access_level": 1, "is_active": True},
            )

            # 2) Crea/busca el usuario en PUBLIC
            user = User.objects.filter(email=email).first()
            if not user:
                user = User(
                    email=email,
                    username=serializer.validated_data.get("document") or email.split("@")[0],
                    first_name=serializer.validated_data.get("first_name", "") or "",
                    last_name=serializer.validated_data.get("last_name", "") or "",
                    company=active_company,
                    role=role_employee,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                )
                user.set_unusable_password()
                user.save()
            else:
                # Si ya existe, debe pertenecer a la misma company
                if user.company_id and user.company_id != active_company.id:
                    raise ValidationError({"email": "Email already used in another company."})
                # Completa datos mínimos si faltan
                changed = False
                if not user.company_id:
                    user.company = active_company
                    changed = True
                if not user.role_id:
                    user.role = role_employee
                    changed = True
                if changed:
                    user.save()

        # 3) Crea el empleado en el TENANT y lo vincula al user
        employee = serializer.save(company=active_company, user=user)
        return employee
