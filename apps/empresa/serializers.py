from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'tenant': {'read_only': True},
            'db_label': {'read_only': True},
            'schema_name': {'required': False},     # 👈 agrega esto
            'domain_url': {'required': False},      # 👈 y esto también
        }
