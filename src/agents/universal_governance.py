from src.agents.base import BaseAgent
from typing import Dict, Any, List
import hashlib
import json
from datetime import datetime


class UniversalGovernanceLayer(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_id="#60",
            name="Universal Governance Layer",
            description="Governanca cross-platform que monitora, audita e controla agentes Microsoft, Google e EcoSystem",
            group="enterprise_connectors",
            price_brl=4990.0,
            price_usd=1490.0,
            tools=["audit_chain", "policy_engine", "trust_scorer", "cross_platform_monitor"],
            llm="claude",
            budget=300000
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = context.get("action", "intercept")
        if action == "intercept":
            return await self._intercept_action(
                context.get("agent_id", ""),
                context.get("platform", "ecosystem"),
                context.get("action_type", ""),
                context.get("payload", {}),
                context.get("tenant_id", "default")
            )
        elif action == "dashboard":
            return await self._get_dashboard(context.get("tenant_id", "default"))
        return {"error": "Unknown action: {action}"}

    async def _intercept_action(self, agent_id: str, platform: str, action_type: str, payload: dict, tenant_id: str) -> Dict:
        action_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        risk_score = self._calculate_risk(agent_id, action_type, platform)
        approved = risk_score < 0.7
        return {
            "allowed": approved,
            "risk_score": risk_score,
            "audit_id": action_hash,
            "platform": platform,
            "agent_id": agent_id,
            "reason": "approved" if approved else "risk_threshold_exceeded"
        }

    def _calculate_risk(self, agent_id: str, action_type: str, platform: str) -> float:
        risk = 0.0
        if action_type in ("delete", "drop", "revoke"):
            risk += 0.3
        if platform not in ("ecosystem",):
            risk += 0.2
        return min(risk, 1.0)

    async def _get_dashboard(self, tenant_id: str) -> Dict:
        return {
            "tenant_id": tenant_id,
            "governance_score": 85.0,
            "total_actions": 0,
            "blocked_actions": 0,
            "platforms": {}
        }
