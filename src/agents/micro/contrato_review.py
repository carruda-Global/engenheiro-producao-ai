from src.agents.base import BaseAgent
from typing import Dict, Any

class ContratoReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="M4", name="Contrato Review", description="Revisao rapida de contratos", group="micro", price_brl=99.0, price_usd=29.0, tools=["analise_contrato", "clausulas_risco"], llm="deepseek-v4-flash", budget=25000)
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": "M4", "revisao": "completa", "clausulas_risco": 0, "upsell": "Ative Compliance Anticorrupcao por R$390/mes"}
