import logging
from integrations.linkedin import LinkedInIntegration
from sales.database import SessionLocal
from sales import pipeline
from sales.linkedin_flow import LinkedInSalesFlow

logger = logging.getLogger(__name__)


class ProspectAgent:
    def __init__(self, linkedin: LinkedInIntegration | None = None):
        self.linkedin = linkedin

    async def search_and_qualify(
        self,
        keywords: str = "",
        industry: str = "",
        title: str = "",
        location: str = "",
        limit: int = 25,
        auto_create_deals: bool = True,
    ) -> dict:
        if not self.linkedin:
            return {"error": "LinkedIn not connected"}

        db = SessionLocal()
        try:
            flow = LinkedInSalesFlow(self.linkedin, db)
            result = await flow.prospect_to_pipeline(
                keywords=keywords,
                industry=industry,
                title=title,
                location=location,
                limit=limit,
                auto_create_deals=auto_create_deals,
            )
            return result
        finally:
            db.close()
