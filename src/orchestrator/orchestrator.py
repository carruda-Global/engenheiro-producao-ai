import logging
from typing import Any, Dict

from .coordinator import CoordinatorAgent
from .graph import create_multi_agent_graph
from .planner import PlannerAgent
from .router import RouterAgent
from .synthesizer import SynthesizerAgent

logger = logging.getLogger(__name__)

_AGENT_CLUSTERS = [
    "aec_core", "aec_specialized", "aec_compliance", "regulatory",
    "microsoft", "cross_sell", "dynamics", "agentforce", "oracle",
    "sap", "coordination", "intelligence", "tech", "self_improvement",
    "enterprise_connectors", "physical_ai",
]

_AGENT_IDS = [
    "architect_agent", "structural_engineer", "mep_engineer", "bim_coordinator",
    "cost_estimator", "scheduler_agent", "quality_inspector", "safety_officer",
    "sustainability_agent", "procurement_agent", "contract_manager", "risk_analyst",
    "permit_agent", "site_supervisor", "materials_agent", "equipment_manager",
    "subcontractor_coordinator", "client_liaison", "document_controller", "bim_modeler",
    "code_compliance", "accessibility_agent", "fire_safety", "structural_reviewer",
    "environmental_agent", "zoning_agent", "historic_preservation", "energy_auditor",
    "lgpd_agent", "nr1_agent", "esg_agent", "tax_agent", "anticorruption_agent",
    "whistleblower_agent", "salary_equality_agent", "onboarding_agent",
    "financial_reconciliation", "cbam_agent", "carbon_inventory", "ifrs_agent",
    "dynamics_sales_agent", "dynamics_finance_agent", "dynamics_hr_agent",
    "agentforce_sdr", "agentforce_contracts", "oracle_erp_agent", "oracle_hcm_agent",
    "sap_compliance_agent", "sap_cbam_agent", "powerbi_agent",
    "meta_orchestrator", "knowledge_graph_agent", "nlp_processor",
    "ml_optimizer", "data_pipeline_agent", "api_gateway_agent",
    "security_agent", "monitoring_agent", "self_healing_agent",
]


class _AgentStub:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = "initialized"
        self.success_rate = 1.0
        self.total_tasks = 0
        self.avg_response_time = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "success_rate": self.success_rate,
            "total_tasks": self.total_tasks,
            "avg_response_time": self.avg_response_time,
        }


class Orchestrator:

    def __init__(self, settings=None):
        self.settings = settings
        self.tenant_id: str = "default"
        self.agents: Dict[str, _AgentStub] = {}
        self._planner = PlannerAgent()
        self._router = RouterAgent()
        self._coordinator = CoordinatorAgent()
        self._synthesizer = SynthesizerAgent()
        self._graph = None

    async def initialize(self) -> None:
        self._graph = create_multi_agent_graph()
        self.agents = {agent_id: _AgentStub(agent_id) for agent_id in _AGENT_IDS}
        logger.info("Orchestrator initialized with %d agents", len(self.agents))

    async def execute_task(self, task: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
        agent_id = task.get("agent_id", "meta_orchestrator")
        agent = self.agents.get(agent_id)

        if agent is None:
            return {"error": f"Agent '{agent_id}' not found", "status": "failed"}

        plan = await self._planner.create_plan(
            query=str(task.get("payload", task)),
            context={"agents": list(self.agents.keys())},
        )

        routed = await self._router.route_batch(plan)

        executor_map = {}
        results = await self._coordinator.execute_parallel(
            tasks=[{"agent": r, "task": p} for r, p in zip(routed, plan)],
            executor_map=executor_map,
        )

        synthesis = await self._synthesizer.synthesize(results)

        agent.total_tasks += 1

        return {
            "status": "completed",
            "agent_id": agent_id,
            "user_id": user_id,
            "result": synthesis,
        }
