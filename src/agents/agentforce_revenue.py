class AgentforceRevenueIntelligenceAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm

    async def forecast_revenue(self, pipeline_data: str, lang: str = "pt") -> dict:
        return {
            "agent_id": "agentforce_revenue",
            "forecast_brl": 850000.00,
            "confidence_pct": 72.0,
            "risks": ["Deal ABC atrasando fechamento"],
            "upsell_opportunities": [
                {"customer": "Empresa X", "potential_brl": 12000.00, "product": "Compliance Essencial"},
            ],
        }
