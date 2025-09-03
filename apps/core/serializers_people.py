# apps/core/serializers_people.py
from rest_framework import serializers

class PeopleListItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    tipo = serializers.CharField()  # "interno" | "contratista"
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    doc_id = serializers.CharField(allow_blank=True, required=False)
    activo = serializers.BooleanField()
    contractor_company = serializers.CharField(allow_null=True, required=False)
    estado_documental = serializers.CharField(allow_null=True, required=False)
    estado_medico = serializers.CharField(allow_null=True, required=False)
    estado_capacitacion = serializers.CharField(allow_null=True, required=False)
    tiene_epp_pendiente = serializers.BooleanField()
