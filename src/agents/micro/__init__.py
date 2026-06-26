from .nr1_diagnostico import NR1DiagnosticoRapido
from .lgpd_scanner import LgpdScanner
from .folha_equidade import FolhaEquidade
from .contrato_review import ContratoReview
from .teams_risk_monitor import TeamsRiskMonitor
from .meeting_minutes import MeetingMinutes
from .pr_lgpd_checker import PrLgpdChecker
from .admissao_checklist import AdmissaoChecklist
from .sales_pipeline_checker import SalesPipelineChecker
from .expense_anomaly import ExpenseAnomaly
from .compliance_score import ComplianceScore
from .lead_qualifier import LeadQualifier
from .code_reviewer import CodeReviewer
from .headcount_alert import HeadcountAlert
from .regulatory_alert import RegulatoryAlert

MICRO_AGENTS = {
    "nr1_diagnostico_rapido": NR1DiagnosticoRapido,
    "lgpd_scanner": LgpdScanner,
    "folha_equidade": FolhaEquidade,
    "contrato_review": ContratoReview,
    "teams_risk_monitor": TeamsRiskMonitor,
    "meeting_minutes": MeetingMinutes,
    "pr_lgpd_checker": PrLgpdChecker,
    "admissao_checklist": AdmissaoChecklist,
    "sales_pipeline_checker": SalesPipelineChecker,
    "expense_anomaly": ExpenseAnomaly,
    "compliance_score": ComplianceScore,
    "lead_qualifier": LeadQualifier,
    "code_reviewer": CodeReviewer,
    "headcount_alert": HeadcountAlert,
    "regulatory_alert": RegulatoryAlert,
}
