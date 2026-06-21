import logging
from typing import Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, Part

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.agents import (
    SpecAnalystAgent,
    ProcurementAgent,
    InventoryAgent,
    LogisticsAgent,
    FieldExecutionAgent,
    BIMCoordinatorAgent,
    RequirementsAnalystAgent,
    EngineeringAssistantAgent,
    WorkSynopsisAgent,
    PhotoIntelligenceAgent,
    RFICreationAgent,
    ComplianceAgent,
)
from .monetization import check_subscription

logger = logging.getLogger(__name__)


SKILL_MAP: dict[str, str] = {
    "spec_analysis": "spec_analyst",
    "procurement": "procurement",
    "inventory": "inventory",
    "logistics": "logistics",
    "field_execution": "field_execution",
    "bim_coordination": "bim_coordinator",
    "requirements_analysis": "requirements_analyst",
    "engineering_assistant": "engineering_assistant",
    "work_synopsis": "work_synopsis",
    "photo_intelligence": "photo_intelligence",
    "rfi_creation": "rfi_creation",
    "compliance": "compliance",
}


class AECAgentExecutor(AgentExecutor):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = DeepSeekClient(settings)
        self._init_agents()

    def _init_agents(self):
        self.agents: dict[str, Any] = {}
        agent_config = self.settings.agents_config

        _map = {
            "spec_analyst": SpecAnalystAgent,
            "procurement": ProcurementAgent,
            "inventory": InventoryAgent,
            "logistics": LogisticsAgent,
            "field_execution": FieldExecutionAgent,
            "bim_coordinator": BIMCoordinatorAgent,
            "requirements_analyst": RequirementsAnalystAgent,
            "engineering_assistant": EngineeringAssistantAgent,
            "work_synopsis": WorkSynopsisAgent,
            "photo_intelligence": PhotoIntelligenceAgent,
            "rfi_creation": RFICreationAgent,
            "compliance": ComplianceAgent,
        }
        for agent_id, agent_class in _map.items():
            if agent_config.get(agent_id, {}).get("enabled", True):
                self.agents[agent_id] = agent_class(self.settings, self.llm)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task_id = context.task_id
        context_id = context.context_id
        user_input = context.get_user_input()

        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task_id,
            context_id=context_id,
        )

        await updater.submit()

        metadata = context.metadata or {}
        requested_skill = metadata.get("skill_id", metadata.get("skill", ""))
        internal_agent_id = SKILL_MAP.get(requested_skill, "spec_analyst")

        api_key = context.call_context.user.api_key if hasattr(context.call_context.user, "api_key") else None
        sub_ok = await check_subscription(self.settings, api_key, internal_agent_id)
        if not sub_ok:
            msg = updater.new_agent_message(
                parts=[Part(text="Assinatura necessária. Acesse https://engenheiro-producao-ai.onrender.com/subscription para adquirir um plano.")]
            )
            await updater.requires_auth(message=msg)
            return

        await updater.start_work()

        try:
            result = self._run_agent(internal_agent_id, user_input)
        except ValueError as e:
            msg = updater.new_agent_message(parts=[Part(text=str(e))])
            await updater.failed(message=msg)
            return

        result_text = self._format_result(result)

        await updater.add_artifact(
            parts=[Part(text=result_text)],
            name="response",
            last_chunk=True,
        )

        complete_msg = updater.new_agent_message(parts=[Part(text=result_text)])
        await updater.complete(message=complete_msg)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )
        msg = updater.new_agent_message(parts=[Part(text="Tarefa cancelada pelo cliente.")])
        await updater.cancel(message=msg)

    def _run_agent(self, agent_id: str, user_input: str) -> dict:
        if agent_id not in self.agents:
            raise ValueError(f"Agente '{agent_id}' não disponível")

        agent = self.agents[agent_id]
        if agent_id == "spec_analyst":
            return agent.analyze_document(user_input)
        elif agent_id == "procurement":
            import json
            try:
                materials = json.loads(user_input)
                if isinstance(materials, dict):
                    materials = [materials]
            except json.JSONDecodeError:
                materials = [{"name": user_input, "quantity": 1, "unit": "un"}]
            return agent.process_order(materials)
        elif agent_id == "inventory":
            import json
            try:
                items = json.loads(user_input)
                if isinstance(items, dict):
                    items = [items]
            except json.JSONDecodeError:
                items = [{"name": user_input, "stock": 10, "min_stock": 20, "daily_use": 2}]
            return agent.check_stock(items)
        elif agent_id == "logistics":
            import json
            try:
                shipment = json.loads(user_input)
            except json.JSONDecodeError:
                shipment = {"product": user_input, "status": "pending"}
            return agent.track_shipment(shipment)
        elif agent_id == "field_execution":
            return agent.generate_field_instructions(user_input)
        elif agent_id == "bim_coordinator":
            return agent.generate_bim_element(user_input)
        elif agent_id == "requirements_analyst":
            return agent.analyze_requirements(user_input)
        elif agent_id == "engineering_assistant":
            return agent.answer_question(user_input)
        elif agent_id == "work_synopsis":
            return agent.generate_synopsis(user_input)
        elif agent_id == "photo_intelligence":
            return agent.analyze_photo(user_input)
        elif agent_id == "rfi_creation":
            return agent.create_rfi(user_input)
        elif agent_id == "compliance":
            return agent.check_compliance(user_input)
        return {"error": "Agente não implementado"}

    def _format_result(self, result: dict) -> str:
        import json
        for key in ["analysis", "order_plan", "stock_analysis", "tracking_analysis",
                     "instructions", "bim_element", "quality_analysis", "answer",
                     "synopsis", "visual_analysis", "rfi_document", "compliance_report"]:
            if key in result:
                return result[key]
        return json.dumps(result, ensure_ascii=False, indent=2)
