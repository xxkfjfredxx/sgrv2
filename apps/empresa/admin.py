# Register your models here.
from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "nit", "sector", "email")
    search_fields = ("name", "nit")
    list_filter = ("sector",)
    ordering = ("name",)
    verbose_name = "Empresa"
    verbose_name_plural = "Empresas"
