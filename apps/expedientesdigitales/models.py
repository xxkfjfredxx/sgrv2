from django.db import models
from apps.empleados.models import Employee
from apps.categoriadocumentos.models import DocumentCategory

class DigitalRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='digital_records')
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT, related_name='digital_records')
    file = models.FileField(upload_to='digital_records/')
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Digital record"
        verbose_name_plural = "Digital records"

    def __str__(self):
        return f"{self.file.name} ({self.employee.first_name} {self.employee.last_name})"
