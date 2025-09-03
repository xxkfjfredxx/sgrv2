# apps/core/views_people.py
from django.db.models import Q, Exists, OuterRef
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response       # <-- IMPORTANTE
from apps.core.pagination import DefaultPagination
from apps.core.serializers_people import PeopleListItemSerializer

from apps.empleados.models import Employee
from apps.contratistas.models import ContractorWorker, ContractorCompany
from apps.epp.models import EPPAssignment
# from apps.salud_ocupacional.models import MedicalExam  # si aún no lo usas, puedes comentarlo

class PeopleListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    serializer_class = PeopleListItemSerializer

    def get_queryset(self):
        # No usamos queryset estándar; devolvemos en list()
        return None

    def list(self, request, *args, **kwargs):
        search = request.query_params.get("search") or request.query_params.get("q")
        tipo = (request.query_params.get("type") or "all").lower()  # all|internal|contractor
        active = request.query_params.get("active")                 # "true"|"false"|None
        contractor_company_id = request.query_params.get("contractor_company")

        # --- Employees internos ---
        emp_qs = Employee.objects.all()
        if search:
            emp_qs = emp_qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)  |
                Q(document__icontains=search)   # ajusta si el campo es 'document'
            )
        if active in ("true", "false"):
            emp_qs = emp_qs.filter(is_active=(active == "true"))

        # Anotación: ¿tiene EPP activo?
        emp_qs = emp_qs.annotate(
            has_open_epp=Exists(
                EPPAssignment.objects.filter(employee_id=OuterRef("id"), status="activo")
            )
        )

        # --- Contratistas (workers de contratista) ---
        cw_qs = ContractorWorker.objects.select_related("contractor_company").all()
        if search:
            cw_qs = cw_qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)  |
                Q(doc_id__icontains=search)
            )
        if active in ("true", "false"):
            cw_qs = cw_qs.filter(is_active=(active == "true"))

        # Si viene contractor_company, validamos que sea int:
        if contractor_company_id:
            try:
                contractor_company_id = int(contractor_company_id)
            except ValueError:
                return Response(
                    {"detail": "contractor_company debe ser numérico."},
                    status=400,
                )
            cw_qs = cw_qs.filter(contractor_company_id=contractor_company_id)

        cw_qs = cw_qs.annotate(
            has_open_epp=Exists(
                EPPAssignment.objects.filter(contractor_worker_id=OuterRef("id"), status="activo")
            )
        )

        # --- Armar lista unificada ---
        items = []
        for e in emp_qs:
            items.append({
                "id": str(e.id),
                "tipo": "interno",
                "first_name": getattr(e, "first_name", ""),
                "last_name": getattr(e, "last_name", ""),
                "doc_id": getattr(e, "document", ""),  # si el campo es 'document'
                "activo": getattr(e, "is_active", True),
                "contractor_company": None,
                "estado_documental": None,   # (TODO)
                "estado_medico": None,       # (TODO)
                "estado_capacitacion": None, # (TODO)
                "tiene_epp_pendiente": bool(getattr(e, "has_open_epp", False)),
            })

        for w in cw_qs:
            items.append({
                "id": str(w.id),
                "tipo": "contratista",
                "first_name": w.first_name,
                "last_name": w.last_name,
                "doc_id": w.doc_id,
                "activo": w.is_active,
                "contractor_company": w.contractor_company.name if w.contractor_company_id else None,
                "estado_documental": None,   # (TODO)
                "estado_medico": None,       # (TODO)
                "estado_capacitacion": None, # (TODO)
                "tiene_epp_pendiente": bool(getattr(w, "has_open_epp", False)),
            })

        # Filtro por tipo en memoria
        if tipo == "internal":
            items = [x for x in items if x["tipo"] == "interno"]
        elif tipo == "contractor":
            items = [x for x in items if x["tipo"] == "contratista"]

        # Orden simple por apellido, nombre
        items.sort(key=lambda x: ((x["last_name"] or "").lower(), (x["first_name"] or "").lower()))

        # Paginación manual
        page = self.paginate_queryset(items)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(items, many=True)
        return Response(ser.data)
