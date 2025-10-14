from django.db import models

class DocumentCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name = "Document category"
        verbose_name_plural = "Document categories"

    def __str__(self):
        return self.name