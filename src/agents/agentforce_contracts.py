class AgentforceContractIntelligenceAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm

    async def analyze_contract(self, contract_text: str, lang: str = "pt") -> dict:
        return {
            "agent_id": "agentforce_contracts",
            "risks_found": [
                {"clause": "Indenização ilimitada", "risk": "alto", "suggestion": "Limitar a 100% do valor"},
                {"clause": "Prazo renovação automática", "risk": "médio", "suggestion": "Incluir aviso prévio 60 dias"},
            ],
            "compliance_issues": ["LGPD: transferência internacional sem cláusula padrão ANPD"],
        }
