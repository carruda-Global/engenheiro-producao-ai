from src.agents.base import BaseAgent
from typing import Dict, Any

class ExpenseAnomalyAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="M10", name="Expense Anomaly", description="Detecta anomalias em despesas", group="micro", price_brl=99.0, price_usd=29.0, tools=["analise_despesas", "anomalias"], llm="deepseek-v4-flash", budget=25000)
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": "M10", "despesas_analisadas": 0, "anomalias": 0, "upsell": "Ative Conciliacao Financeira por R$790/mes"}
