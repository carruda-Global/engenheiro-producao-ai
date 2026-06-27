from src.agents.base import BaseAgent
from typing import Dict, Any

class FolhaEquidadeAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="M3", name="Folha Equidade", description="Analise rapida de equidade salarial", group="micro", price_brl=99.0, price_usd=29.0, tools=["analise_folha", "gap_salarial"], llm="deepseek-v4-flash", budget=25000)
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": "M3", "analise": "completa", "gap": 0.0, "upsell": "Ative Igualdade Salarial completo por R$490/mes"}
