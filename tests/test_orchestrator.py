import pytest
from src.orchestrator import Orchestrator


@pytest.mark.unit
class TestOrchestrator:
    def test_init_loads_enabled_agents(self, settings):
        orchestrator = Orchestrator(settings)
        for agent_id in [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
            "bim_coordinator", "requirements_analyst",
            "engineering_assistant", "work_synopsis",
            "photo_intelligence", "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "esg_ifrs",
            "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ]:
            assert agent_id in orchestrator.agents

    def test_health_check_returns_dict(self, settings):
        orchestrator = Orchestrator(settings)
        result = orchestrator.health_check()
        assert result["status"] == "healthy"
        assert len(result["agents"]) == 21

    def test_run_agent_valid(self, settings, llm_mock):
        orchestrator = Orchestrator(settings)
        orchestrator.agents["spec_analyst"].llm = llm_mock
        result = orchestrator.run_agent("spec_analyst", {"document": "teste"})
        assert isinstance(result, dict)

    def test_run_agent_invalid(self, settings):
        orchestrator = Orchestrator(settings)
        with pytest.raises(ValueError, match="Agent 'invalid' nao encontrado"):
            orchestrator.run_agent("invalid", {})

    def test_process_workflow_returns_list(self, settings, llm_mock):
        orchestrator = Orchestrator(settings)
        for agent in orchestrator.agents.values():
            agent.llm = llm_mock
        result = orchestrator.process_workflow({"document": "Projeto estrutural"})
        assert isinstance(result, list)
