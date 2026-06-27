from src.agents.base import BaseAgent
from typing import Dict, Any

class NR1RapidAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="M1", name="NR-1 Diagnostico Rapido", description="Diagnostico rapido de riscos psicossociais NR-1", group="micro", price_brl=99.0, price_usd=29.0, tools=["questionario_rapido", "score_psicossocial"], llm="gemini", budget=25000)
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": "M1", "diagnostico": "rapido", "score": 0.5, "upsell": "Ative o NR-1 completo por R$390/mes"}
