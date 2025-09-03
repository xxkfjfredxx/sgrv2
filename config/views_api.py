from rest_framework.routers import DefaultRouter
from django.urls import path

# Importa tus ViewSets y la función summary
from apps.empresa.views import CompanyViewSet
from apps.empleados.views import (
    EmployeeViewSet,
    EmployeeDocumentViewSet,
    DocumentTypeViewSet,
)
from apps.vinculaciones.views import EmploymentLinkViewSet
from apps.historial.views import WorkHistoryViewSet
from apps.auditoria.views import (
    SystemAuditViewSet,
    AuditChecklistViewSet,
    AuditItemViewSet,
    AuditExecutionViewSet,
    AuditResultViewSet,
    AuditFindingViewSet,
)
from apps.catalogos.views import BranchViewSet, PositionViewSet, WorkAreaViewSet
from apps.usuarios.views import UserViewSet, UserRoleViewSet
from apps.salud_ocupacional.views import MedicalExamViewSet
from apps.ausentismo.views import AbsenceViewSet
from apps.capacitaciones.views import (
    TrainingSessionViewSet,
    TrainingSessionAttendanceViewSet,
)
from apps.seguridad_industrial.views import (
    WorkAccidentViewSet,
    WorkAtHeightPermitViewSet,
)
from apps.reintegro.views import ReintegroViewSet
from apps.pausas_activas.views import (
    ActivePauseSessionViewSet,
    ActivePauseAttendanceViewSet,
)
from apps.indicadores.views import (
    IndicatorViewSet,
    IndicatorResultViewSet,
    indicator_summary,
)
from apps.alertas.views import DocumentAlertViewSet
from apps.acciones_correctivas.views import (
    ImprovementPlanViewSet,
    ActionItemViewSet,
    RiskActionViewSet,
)
from apps.riesgos.views import ControlEvidenceViewSet, ControlFollowUpViewSet
from apps.sst_policies.views import SSTPolicyViewSet, PolicyAcceptanceViewSet
from apps.inspecciones.views import (
    InspectionTemplateViewSet,
    InspectionItemViewSet,
    InspectionViewSet,
    InspectionResponseViewSet,
)
from apps.emergencies.views import (
    EmergencyBrigadeMemberViewSet,
    EmergencyEquipmentViewSet,
    EmergencyDrillViewSet,
)
from apps.epp.views import EPPItemViewSet, EPPAssignmentViewSet
from apps.riesgos.views import AreaViewSet, HazardViewSet, RiskAssessmentViewSet
from apps.accesos.views import AccessLogViewSet, RiskAcceptanceFormViewSet
from apps.stakeholders.views import StakeholderViewSet
from apps.legal.views import LegalRequirementViewSet
from apps.suggestions.views import SuggestionBoxViewSet
from apps.contratos.views import ContractViewSet
from apps.objectives.views import SSTObjectiveViewSet, SSTGoalViewSet
from apps.actividades.views import ActivityViewSet
from apps.safety.views import SignageInventoryViewSet, VaccinationRecordViewSet
from apps.equipment.views import EquipmentInventoryViewSet, EquipmentInspectionViewSet

router = DefaultRouter()

router.register(r"signage", SignageInventoryViewSet, basename="signage")
router.register(r"vaccinations", VaccinationRecordViewSet, basename="vaccinations")

router.register(r"control-evidences", ControlEvidenceViewSet)
router.register(r"control-followups", ControlFollowUpViewSet)

router.register(r"equipment-inventory", EquipmentInventoryViewSet)
router.register(r"equipment-inspections", EquipmentInspectionViewSet)

router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"employees", EmployeeViewSet, basename="employees")  # ✅
router.register(r"employment-links", EmploymentLinkViewSet)
router.register(r"work-history", WorkHistoryViewSet)
router.register(r"branches", BranchViewSet)
router.register(r"positions", PositionViewSet)
router.register(r"work-areas", WorkAreaViewSet)
router.register(r"document-types", DocumentTypeViewSet, basename="document-type")   
router.register(r"users", UserViewSet)
router.register(r"user-roles", UserRoleViewSet)
router.register(r"documents", EmployeeDocumentViewSet, basename="employee-document")
router.register(r"medical-exams", MedicalExamViewSet)
router.register(r"absences", AbsenceViewSet)
router.register(r"training-sessions", TrainingSessionViewSet)
router.register(r"training-attendance", TrainingSessionAttendanceViewSet)
router.register(r"work-accidents", WorkAccidentViewSet)
router.register(r"improvement-plans", ImprovementPlanViewSet)
router.register(r"action-items", ActionItemViewSet)
router.register(r"work-at-height-permits", WorkAtHeightPermitViewSet)
router.register(r"reintegrations", ReintegroViewSet)
router.register(r"pausas-sessions", ActivePauseSessionViewSet)
router.register(r"pausas-attendance", ActivePauseAttendanceViewSet)
router.register(r"indicators", IndicatorViewSet)
router.register(r"indicator-results", IndicatorResultViewSet)
router.register(r"document-alerts", DocumentAlertViewSet)
router.register(r"stakeholders", StakeholderViewSet)
router.register(r"legal-requirements", LegalRequirementViewSet)
router.register(r"sst-policies", SSTPolicyViewSet)
router.register(r"policy-acceptances", PolicyAcceptanceViewSet)
router.register(r"suggestions", SuggestionBoxViewSet)
router.register(r"emergency-brigade", EmergencyBrigadeMemberViewSet)
router.register(r"emergency-equipment", EmergencyEquipmentViewSet)
router.register(r"emergency-drills", EmergencyDrillViewSet)
router.register(r"contracts", ContractViewSet)
router.register(r"sst-objectives", SSTObjectiveViewSet)
router.register(r"sst-goals", SSTGoalViewSet)
router.register(r"risk-actions", RiskActionViewSet)
router.register(r"system-audit", SystemAuditViewSet)
router.register(r"activities", ActivityViewSet)
router.register(r"audit-checklists", AuditChecklistViewSet)
router.register(r"audit-items", AuditItemViewSet)
router.register(r"audit-executions", AuditExecutionViewSet)
router.register(r"audit-results", AuditResultViewSet)
router.register(r"audit-findings", AuditFindingViewSet)
router.register(r"inspection-templates", InspectionTemplateViewSet)
router.register(r"inspection-items", InspectionItemViewSet)
router.register(r"inspections", InspectionViewSet)
router.register(r"inspection-responses", InspectionResponseViewSet)
router.register(r"epp-items", EPPItemViewSet)
router.register(r"epp-assignments", EPPAssignmentViewSet)
router.register(r"areas", AreaViewSet)
router.register(r"hazards", HazardViewSet)
router.register(r"risk-assessments", RiskAssessmentViewSet)
router.register(r"access-logs", AccessLogViewSet)
router.register(r"risk-acceptances", RiskAcceptanceFormViewSet)

# 2) Insertamos summary ANTES de router.urls
urlpatterns = [
    path("indicators/summary/", indicator_summary, name="indicator-summary"),
] + router.urls
