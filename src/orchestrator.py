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
        if agent_config.get("spec_analyst", {}).get("enabled"):
            self.agents["spec_analyst"] = SpecAnalystAgent(self.settings, self.llm)
        if agent_config.get("procurement", {}).get("enabled"):
            self.agents["procurement"] = ProcurementAgent(self.settings, self.llm)
        if agent_config.get("inventory", {}).get("enabled"):
            self.agents["inventory"] = InventoryAgent(self.settings, self.llm)
        if agent_config.get("logistics", {}).get("enabled"):
            self.agents["logistics"] = LogisticsAgent(self.settings, self.llm)
        if agent_config.get("field_execution", {}).get("enabled"):
            self.agents["field_execution"] = FieldExecutionAgent(
                self.settings, self.llm
            )

        self.logger.info(
            "Agents initialized: %s", ", ".join(self.agents.keys())
        )

    def process_workflow(self, initial_input: dict) -> list[dict]:
        results = []
        current_context = initial_input

        if "spec_analyst" in self.agents:
            doc_text = current_context.get("document", "")
            if doc_text:
                result = self.agents["spec_analyst"].analyze_document(doc_text)
                results.append(result)
                current_context["last_analysis"] = result
                self.logger.info("SpecAnalystAgent executed")

        if "procurement" in self.agents:
            specs = current_context.get("last_analysis", {}).get("analysis", "")
            if specs and self._needs_procurement(specs):
                materials = self._extract_materials(specs)
                result = self.agents["procurement"].process_order(materials)
                results.append(result)
                current_context["last_order"] = result
                self.logger.info("ProcurementAgent executed")

        if "inventory" in self.agents:
            order_info = current_context.get("last_order", {})
            if order_info:
                items = self._build_stock_items(order_info)
                result = self.agents["inventory"].check_stock(items)
                results.append(result)
                current_context["last_stock"] = result
                self.logger.info("InventoryAgent executed")

        if "logistics" in self.agents:
            stock_info = current_context.get("last_stock", {})
            if stock_info:
                result = self.agents["logistics"].track_shipment(
                    {"status": "pending", "product": "materials"}
                )
                results.append(result)
                self.logger.info("LogisticsAgent executed")

        if "field_execution" in self.agents:
            project_specs = current_context.get("document", "")
            if project_specs:
                result = self.agents["field_execution"].generate_field_instructions(
                    project_specs
                )
                results.append(result)
                self.logger.info("FieldExecutionAgent executed")

        return results

    def run_agent(self, agent_id: str, input_data: dict) -> dict:
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' nao encontrado")

        agent = self.agents[agent_id]

        if agent_id == "spec_analyst":
            return agent.analyze_document(input_data.get("document", ""))
        elif agent_id == "procurement":
            return agent.process_order(input_data.get("materials", []))
        elif agent_id == "inventory":
            return agent.check_stock(input_data.get("items", []))
        elif agent_id == "logistics":
            return agent.track_shipment(input_data.get("shipment", {}))
        elif agent_id == "field_execution":
            return agent.generate_field_instructions(
                input_data.get("specs", "")
            )

        return {"error": "Agente nao implementado"}

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
