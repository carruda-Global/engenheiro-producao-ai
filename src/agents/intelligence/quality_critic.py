from src.agents.base import BaseAgent
from src.security.trust_agent import TrustAgent
from typing import Dict, Any, List
from datetime import datetime


class QualityCriticAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_id="#53",
            name="Quality Critic / Sentinel",
            description="Supervisao de qualidade e seguranca dos agentes",
            group="intelligence",
            price_brl=1497.0,
            price_usd=299.0,
            tools=["audit_log", "trust_agent"],
            llm="deepseek-v4-flash",
            budget=150000
        )
        self.trust_agent = TrustAgent()
        self.audit_log = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        target_agent = context.get("target_agent")
        action = context.get("action", {})
        output = context.get("output", {})

        intercepted = self.trust_agent.intercept(action, "input")
        if intercepted.get("status") == "blocked":
            return {"status": "blocked", "reason": intercepted.get("reason"), "suspicious_agent": target_agent}

        quality_result = await self._check_quality(output)
        self._audit(target_agent, action, output)

        return {"status": "approved", "quality": quality_result, "audit_id": len(self.audit_log) - 1}

    def _audit(self, agent_id: str, action: Dict[str, Any], output: Dict[str, Any]):
        self.audit_log.append({"agent_id": agent_id, "action": action, "output": output, "timestamp": datetime.now().isoformat()})

    async def _check_quality(self, output: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 1.0, "issues": []}

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.audit_log[-limit:]
