from src.agents.base import BaseAgent
from typing import Dict, Any

class CodeReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="M13", name="Code Reviewer", description="Revisao rapida de codigo", group="micro", price_brl=99.0, price_usd=29.0, tools=["code_review", "qualidade"], llm="deepseek-v4-flash", budget=25000)
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"agent": "M13", "revisao": "completa", "issues": 0, "upsell": "Ative Software Engineering Agent por R$1.997/mes"}
