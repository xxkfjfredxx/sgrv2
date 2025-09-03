from django.db import models
from apps.empresa.models import Company
from apps.usuarios.models import User
from apps.acciones_correctivas.models import ActionItem
from apps.utils.mixins import AuditMixin

class SystemAudit(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    affected_table = models.CharField(max_length=100)
    record_id = models.IntegerField()
    previous_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_audit"
        ordering = ["-created_at"]

    def __str__(self):
        base = f"{self.action} on {self.affected_table}"
        return f"{base} by {self.user}" if self.user else base


class AuditChecklist(AuditMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "audit_checklist"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class AuditItem(AuditMixin, models.Model):
    checklist = models.ForeignKey(
        AuditChecklist, on_delete=models.CASCADE, related_name="items"
    )
    question = models.CharField(max_length=300)
    expected_result = models.CharField(max_length=300, blank=True)
    evidence_required = models.BooleanField(default=False)

    class Meta:
        db_table = "audit_item"
        ordering = ["id"]

    def __str__(self):
        return f"{self.checklist.name} – {self.question[:40]}"


class AuditExecution(AuditMixin, models.Model):
    checklist = models.ForeignKey(AuditChecklist, on_delete=models.CASCADE)
    auditor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=50, default="Abierta"
    )  # Abierta / Cerrada / En seguimiento
    comments = models.TextField(blank=True)

    class Meta:
        db_table = "audit_execution"
        ordering = ["-date"]

    def __str__(self):
        return f"Auditoría {self.checklist.name} – {self.date}"


class AuditResult(AuditMixin, models.Model):
    execution = models.ForeignKey(
        AuditExecution, on_delete=models.CASCADE, related_name="results"
    )
    item = models.ForeignKey(AuditItem, on_delete=models.CASCADE)
    result = models.CharField(
        max_length=30,
        choices=[
            ("cumple", "Cumple"),
            ("no_cumple", "No cumple"),
            ("parcial", "Cumple parcialmente"),
        ],
    )
    evidence_file = models.FileField(upload_to="audit_evidence/", blank=True, null=True)
    observation = models.TextField(blank=True)

    class Meta:
        db_table = "audit_result"
        ordering = ["item_id"]

    def __str__(self):
        return f"{self.execution} – {self.item.question[:30]}: {self.result}"


class AuditFinding(AuditMixin, models.Model):
    execution = models.ForeignKey(
        AuditExecution, on_delete=models.CASCADE, related_name="findings"
    )
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[("Leve", "Leve"), ("Moderado", "Moderado"), ("Crítico", "Crítico")],
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("abierto", "Abierto"),
            ("cerrado", "Cerrado"),
            ("seguimiento", "En seguimiento"),
        ],
        default="abierto",
    )
    closing_evidence = models.FileField(
        upload_to="audit_findings_closing/", blank=True, null=True
    )
    action_item = models.ForeignKey(
        ActionItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Acción correctiva asociada (si aplica)",
    )

    class Meta:
        db_table = "audit_finding"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Hallazgo {self.severity} ({self.status})"
