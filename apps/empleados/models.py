from django.db import models
from django.conf import settings
import os
from datetime import datetime
from apps.utils.mixins import AuditMixin
from apps.empresa.models import Company


class Employee(AuditMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    document = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    eps = models.CharField(max_length=100, blank=True, null=True)
    afp = models.CharField(max_length=100, blank=True, null=True)
    compensation_fund = models.CharField(max_length=100, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    phone_contact = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    ethnicity = models.CharField(max_length=50, blank=True, null=True)
    socioeconomic_stratum = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "employees"
        ordering = ["first_name", "last_name"]
        indexes = [# los indexes ayudan a mejorar el rendimiento en las consultas
            models.Index(fields=['first_name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['address']),
            models.Index(fields=['phone_contact']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

# ──────────────────────────────────────────────────────────────
#  NUEVO  ▸  Categoría de documentos
# ──────────────────────────────────────────────────────────────
class DocumentCategory(AuditMixin, models.Model):
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────────────────────
#  Modificado ▸ DocumentType
# ──────────────────────────────────────────────────────────────
class DocumentType(AuditMixin, models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)

    # NUEVOS CAMPOS ↓↓↓
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name="types",
        null=True,
        blank=True,
    )
    requires_expiration = models.BooleanField(default=False)
    default_expiry_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Si se deja vacío y el documento vence, el usuario ingresará la fecha manualmente.",
    )

    class Meta:
        db_table = "document_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


def document_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    doc_type = instance.document_type.name.lower().replace(" ", "_")
    date_path = datetime.now().strftime("%Y/%m/%d")
    filename = f"{doc_type}-emp{instance.employee.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join("documents", doc_type, date_path, filename)


class EmployeeDocument(AuditMixin, models.Model):
    employee = models.ForeignKey(
        "empleados.Employee", on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.ForeignKey("DocumentType", on_delete=models.PROTECT)
    file = models.FileField(upload_to=document_upload_path)
    company = models.ForeignKey(
        "empresa.Company", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_global = models.BooleanField(default=False)

    class Meta:
        db_table = "employee_documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} – {self.document_type}"
