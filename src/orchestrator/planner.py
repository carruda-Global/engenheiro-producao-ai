import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PlannerAgent:

    def __init__(self, llm_client=None):
        self.llm = llm_client

    async def decompose(self, query: str, available_agents: List[Dict]) -> List[Dict[str, Any]]:
        logger.info(f"Decomposing query: {query[:50]}...")
        tasks = [{"step": 1, "agent": "auto", "task": query, "priority": 1}]
        return tasks

    async def create_plan(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await self.decompose(query, context.get("agents", []))
