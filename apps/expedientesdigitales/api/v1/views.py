from rest_framework import viewsets, filters
from django.utils.timezone import now
from django.db.models import Q
from apps.utils.auditlogmimix import AuditLogMixin
from apps.expedientesdigitales.models import DigitalRecord
from .serializers import DigitalRecordSerializer

class DigitalRecordViewSet(AuditLogMixin, viewsets.ModelViewSet):
    queryset = DigitalRecord.objects.select_related("employee", "category").all()
    serializer_class = DigitalRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("employee__document", "employee__first_name", "category__name")
    ordering_fields = ("created_at", "expiry_date")

    def get_queryset(self):
        qs = super().get_queryset()
        # Optional: scope to active_company if model does not already do it at DB level
        active_company = getattr(self.request, "active_company", None)
        if active_company:
            qs = qs.filter(employee__company_id=active_company.id)

        employee_id = self.request.query_params.get("employee")
        category_id = self.request.query_params.get("category")
        active = self.request.query_params.get("active")

        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if active in ("true", "false"):
            today = now().date()
            if active == "true":
                qs = qs.filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=today))
            else:
                qs = qs.filter(expiry_date__lt=today)
        return qs
