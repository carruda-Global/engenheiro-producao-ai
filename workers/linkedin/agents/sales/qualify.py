import logging
from datetime import datetime
from sales.database import SessionLocal
from sales import models, pipeline, scoring
from integrations.site.analytics import SiteAnalytics

logger = logging.getLogger(__name__)


class LeadQualifier:
    def __init__(self):
        self.db = SessionLocal()
        self.analytics = SiteAnalytics()

    def close(self):
        self.db.close()
        self.analytics.close()

    async def score_lead(self, lead_id: int) -> dict:
        lead = pipeline.score_lead(self.db, lead_id)
        if not lead:
            return {"error": "Lead not found"}

        behavior = self.analytics.get_lead_score_by_behavior(lead_id)

        total_score = min(lead.score + behavior.get("behavior_score", 0), 100)
        label = "hot" if total_score >= 80 else "warm" if total_score >= 60 else "tepid" if total_score >= 40 else "cold"

        result = {
            "lead_id": lead.id,
            "name": lead.name,
            "bant_score": lead.score,
            "behavior_score": behavior.get("behavior_score", 0),
            "total_score": total_score,
            "label": label,
        }

        if total_score >= 80:
            lead.status = models.LeadStatus.QUALIFIED.value
            self.db.commit()
            result["action"] = "schedule_demo"
            result["message"] = "Lead qualificado para demonstracao"
        elif total_score >= 60:
            result["action"] = "start_nurture"
            result["message"] = "Iniciar nutricao automatica"
        else:
            result["action"] = "continue_nurture"
            result["message"] = "Continuar nutricao"

        return result

    async def get_qualified_for_demo(self, min_score: int = 80) -> list[dict]:
        leads = pipeline.get_leads_by_score(self.db, min_score=min_score)
        return [
            {
                "id": l.id,
                "name": l.name,
                "company": l.company,
                "score": l.score,
                "email": l.email,
                "phone": l.phone,
            }
            for l in leads
        ]
