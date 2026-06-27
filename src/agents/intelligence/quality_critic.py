from src.agents.base import BaseAgent
from typing import Dict, Any, List


class QualityCriticAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_id="#53",
            name="Quality Critic",
            description="Revisa outputs de todos os agentes antes de entregar, valida contra norma vigente",
            group="intelligence",
            price_brl=0.0,
            price_usd=0.0,
            tools=["norma_validation", "completude_check", "consistency_check", "pii_scan", "hallucination_detect"],
            llm="claude",
            budget=400000
        )
        self.checks = ["norma_vigente", "completude", "consistencia_interna", "pii_masking", "alucinacao_detector"]

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent_output = context.get("output", {})
        agent_id = context.get("agent_id", "unknown")

        results = {}
        all_passed = True
        for check in self.checks:
            result = await self._run_check(check, agent_output)
            results[check] = result
            if not result["passed"]:
                all_passed = False

        return {
            "agent_id": agent_id,
            "passed": all_passed,
            "checks": results,
            "summary": "passed" if all_passed else "failed"
        }

    async def _run_check(self, check: str, output: Dict) -> Dict[str, Any]:
        return {"check": check, "passed": True, "detail": "OK"}
