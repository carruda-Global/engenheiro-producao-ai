import hashlib
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TrustAgent:

    def __init__(self):
        self.belief_states: Dict[str, float] = {}
        self.anomaly_threshold = 0.3

    async def evaluate(self, agent_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        trust_score = self.belief_states.get(agent_id, 0.8)
        risk_factors = self._analyze_risk(action, context)
        adjusted_score = trust_score - sum(risk_factors.values())

        self.belief_states[agent_id] = adjusted_score
        is_trusted = adjusted_score >= self.anomaly_threshold

        return {
            "agent_id": agent_id,
            "trust_score": round(adjusted_score, 3),
            "is_trusted": is_trusted,
            "risk_factors": risk_factors
        }

    def _analyze_risk(self, action: str, context: Dict[str, Any]) -> Dict[str, float]:
        factors = {}
        if context.get("data_sensitivity") == "high":
            factors["data_sensitivity"] = 0.2
        if action in ("delete", "revoke"):
            factors["action_risk"] = 0.3
        if context.get("anomalous_pattern"):
            factors["anomalous"] = 0.4
        return factors
