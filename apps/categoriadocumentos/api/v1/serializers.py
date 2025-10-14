from rest_framework import serializers
from apps.categoriadocumentos.models import DocumentCategory

class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ("id", "name", "slug")
