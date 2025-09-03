# apps/empleados/admin.py
from django.contrib import admin
from .models import DocumentCategory, DocumentType, EmployeeDocument


@admin.register(DocumentCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(DocumentType)
class DocTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "category",
        "requires_expiration",
        "default_expiry_months",
    )
    list_filter = ("category", "requires_expiration")
    search_fields = ("code", "name")


admin.site.register(EmployeeDocument)
