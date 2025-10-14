from rest_framework import viewsets
from django_ratelimit.decorators import ratelimit
from apps.categoriadocumentos.models import DocumentCategory
from .serializers import DocumentCategorySerializer

class DocumentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentCategory.objects.all().order_by("name")
    serializer_class = DocumentCategorySerializer

    @ratelimit(key="ip", rate="15/m", method="GET", block=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
