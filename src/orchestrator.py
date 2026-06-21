import logging
from typing import Any

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


class Orchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = DeepSeekClient(settings)
        self.logger = logging.getLogger(__name__)

        self.agents: dict[str, Any] = {}
        self._init_agents()

    def _init_agents(self):
        agent_config = self.settings.agents_config

        _agent_map = {
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

        for agent_id, agent_class in _agent_map.items():
            if agent_config.get(agent_id, {}).get("enabled", True):
                self.agents[agent_id] = agent_class(self.settings, self.llm)

        self.logger.info(
            "Agents initialized: %s", ", ".join(self.agents.keys())
        )

    def process_workflow(self, initial_input: dict) -> list[dict]:
        results = []
        current_context = initial_input

        workflow_chain = [
            "spec_analyst",
            "procurement",
            "inventory",
            "logistics",
            "field_execution",
            "bim_coordinator",
            "requirements_analyst",
            "engineering_assistant",
            "work_synopsis",
            "photo_intelligence",
            "rfi_creation",
            "compliance",
        ]

        for agent_id in workflow_chain:
            if agent_id in self.agents:
                result = self._run_agent_step(agent_id, current_context)
                if result:
                    results.append(result)
                    current_context[f"last_{agent_id}"] = result
                    self.logger.info("%s executed", agent_id)

        return results

    def run_agent(self, agent_id: str, input_data: dict) -> dict:
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' nao encontrado")

        agent = self.agents[agent_id]

        dispatch = {
            "spec_analyst": lambda: agent.analyze_document(input_data.get("document", "")),
            "procurement": lambda: agent.process_order(input_data.get("materials", [])),
            "inventory": lambda: agent.check_stock(input_data.get("items", [])),
            "logistics": lambda: agent.track_shipment(input_data.get("shipment", {})),
            "field_execution": lambda: agent.generate_field_instructions(input_data.get("specs", "")),
            "bim_coordinator": lambda: agent.generate_bim_element(input_data.get("description", "")),
            "requirements_analyst": lambda: agent.analyze_requirements(input_data.get("requirements", "")),
            "engineering_assistant": lambda: agent.answer_question(input_data.get("question", ""), input_data.get("context", "")),
            "work_synopsis": lambda: agent.generate_synopsis(input_data.get("task_data", "")),
            "photo_intelligence": lambda: agent.analyze_photo(input_data.get("photo_description", "")),
            "rfi_creation": lambda: agent.create_rfi(input_data.get("question", ""), input_data.get("context", "")),
            "compliance": lambda: agent.check_compliance(input_data.get("project_data", "")),
        }

        handler = dispatch.get(agent_id)
        if handler:
            return handler()
        return {"error": "Agente nao implementado"}

    def _run_agent_step(self, agent_id: str, context: dict) -> dict | None:
        agent = self.agents[agent_id]
        if agent_id == "spec_analyst":
            doc = context.get("document", "")
            return agent.analyze_document(doc) if doc else None
        elif agent_id == "procurement":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            if analysis and self._needs_procurement(analysis):
                materials = self._extract_materials(analysis)
                return agent.process_order(materials)
        elif agent_id == "inventory":
            order = context.get("last_procurement", {})
            if order:
                items = self._build_stock_items(order)
                return agent.check_stock(items)
        elif agent_id == "logistics":
            stock = context.get("last_inventory", {})
            if stock:
                return agent.track_shipment(
                    {"status": "pending", "product": "materials"}
                )
        elif agent_id == "field_execution":
            doc = context.get("document", "")
            return agent.generate_field_instructions(doc) if doc else None
        elif agent_id == "bim_coordinator":
            doc = context.get("document", "")
            return agent.generate_bim_element(doc[:500]) if doc else None
        elif agent_id == "requirements_analyst":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            return agent.analyze_requirements(analysis) if analysis else None
        elif agent_id == "engineering_assistant":
            doc = context.get("document", "")
            return agent.answer_question("Sumarize este documento", doc) if doc else None
        elif agent_id == "work_synopsis":
            doc = context.get("document", "")
            return agent.generate_synopsis(doc[:500]) if doc else None
        elif agent_id == "photo_intelligence":
            doc = context.get("document", "")
            return agent.analyze_photo(doc[:500]) if doc else None
        elif agent_id == "rfi_creation":
            analysis = context.get("last_spec_analyst", {}).get("analysis", "")
            return agent.create_rfi("Duvida sobre especificacao", analysis) if analysis else None
        elif agent_id == "compliance":
            doc = context.get("document", "")
            return agent.check_compliance(doc) if doc else None
        return None

    def _needs_procurement(self, analysis: str) -> bool:
        keywords = ["material", "compra", "fornecedor", "insumo", "equipamento"]
        return any(k in analysis.lower() for k in keywords)

    def _extract_materials(self, analysis: str) -> list[dict]:
        return [{"name": "Material identificado", "quantity": 1, "unit": "un"}]

    def _build_stock_items(self, order_info: dict) -> list[dict]:
        return [
            {
                "name": "Item do pedido",
                "stock": 10,
                "min_stock": 20,
                "daily_use": 2,
            }
        ]

    def health_check(self) -> dict:
        return {
            "status": "healthy",
            "agents": list(self.agents.keys()),
            "llm_connected": self.llm.health_check(),
        }
