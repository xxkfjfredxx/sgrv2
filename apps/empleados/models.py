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