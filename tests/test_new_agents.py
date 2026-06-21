import pytest
from unittest.mock import MagicMock

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient


@pytest.fixture
def settings():
    s = Settings()
    s.deepseek_api_key = "test-key"
    return s


@pytest.fixture
def llm_mock():
    mock = MagicMock(spec=DeepSeekClient)
    mock.chat.return_value = "Analise concluida com sucesso."
    return mock


@pytest.mark.unit
class TestBIMCoordinatorAgent:
    def test_generate_bim_element_returns_dict(self, settings, llm_mock):
        from src.agents.bim_coordinator import BIMCoordinatorAgent
        agent = BIMCoordinatorAgent(settings, llm_mock)
        result = agent.generate_bim_element("Criar parede de concreto 3m x 2.8m")
        assert isinstance(result, dict)
        assert "bim_element" in result

    def test_clash_detection_returns_string(self, settings, llm_mock):
        from src.agents.bim_coordinator import BIMCoordinatorAgent
        agent = BIMCoordinatorAgent(settings, llm_mock)
        result = agent.clash_detection("Projeto estrutural com vigas e pilares")
        assert isinstance(result, str)


@pytest.mark.unit
class TestRequirementsAnalystAgent:
    def test_analyze_requirements_returns_dict(self, settings, llm_mock):
        from src.agents.requirements_analyst import RequirementsAnalystAgent
        agent = RequirementsAnalystAgent(settings, llm_mock)
        result = agent.analyze_requirements("Fundacao deve suportar carga de 50kN")
        assert isinstance(result, dict)
        assert "quality_analysis" in result

    def test_check_consistency_returns_string(self, settings, llm_mock):
        from src.agents.requirements_analyst import RequirementsAnalystAgent
        agent = RequirementsAnalystAgent(settings, llm_mock)
        result = agent.check_consistency("Req A", "Req B")
        assert isinstance(result, str)


@pytest.mark.unit
class TestEngineeringAssistantAgent:
    def test_answer_question_returns_dict(self, settings, llm_mock):
        from src.agents.engineering_assistant import EngineeringAssistantAgent
        agent = EngineeringAssistantAgent(settings, llm_mock)
        result = agent.answer_question("O que e NBR-6118?")
        assert isinstance(result, dict)
        assert "answer" in result

    def test_summarize_document_returns_string(self, settings, llm_mock):
        from src.agents.engineering_assistant import EngineeringAssistantAgent
        agent = EngineeringAssistantAgent(settings, llm_mock)
        result = agent.summarize_document("Documento tecnico longo")
        assert isinstance(result, str)


@pytest.mark.unit
class TestWorkSynopsisAgent:
    def test_generate_synopsis_returns_dict(self, settings, llm_mock):
        from src.agents.work_synopsis import WorkSynopsisAgent
        agent = WorkSynopsisAgent(settings, llm_mock)
        result = agent.generate_synopsis("Defeito: trinca na viga V-03")
        assert isinstance(result, dict)
        assert "synopsis" in result

    def test_summarize_project_status_returns_string(self, settings, llm_mock):
        from src.agents.work_synopsis import WorkSynopsisAgent
        agent = WorkSynopsisAgent(settings, llm_mock)
        result = agent.summarize_project_status("Obra avancou 15% esta semana")
        assert isinstance(result, str)


@pytest.mark.unit
class TestPhotoIntelligenceAgent:
    def test_analyze_photo_returns_dict(self, settings, llm_mock):
        from src.agents.photo_intelligence import PhotoIntelligenceAgent
        agent = PhotoIntelligenceAgent(settings, llm_mock)
        result = agent.analyze_photo("Foto do canteiro com trabalhadores sem EPI")
        assert isinstance(result, dict)
        assert "visual_analysis" in result

    def test_compare_with_schedule_returns_string(self, settings, llm_mock):
        from src.agents.photo_intelligence import PhotoIntelligenceAgent
        agent = PhotoIntelligenceAgent(settings, llm_mock)
        result = agent.compare_with_schedule("Foto da fundacao", "30% concluido")
        assert isinstance(result, str)


@pytest.mark.unit
class TestRFICreationAgent:
    def test_create_rfi_returns_dict(self, settings, llm_mock):
        from src.agents.rfi_creation import RFICreationAgent
        agent = RFICreationAgent(settings, llm_mock)
        result = agent.create_rfi("Qual a resistencia do concreto?")
        assert isinstance(result, dict)
        assert "rfi_document" in result

    def test_search_specification_returns_string(self, settings, llm_mock):
        from src.agents.rfi_creation import RFICreationAgent
        agent = RFICreationAgent(settings, llm_mock)
        result = agent.search_specification("Resistencia minima?", "NBR-6118")
        assert isinstance(result, str)


@pytest.mark.unit
class TestComplianceAgent:
    def test_check_compliance_returns_dict(self, settings, llm_mock):
        from src.agents.compliance import ComplianceAgent
        agent = ComplianceAgent(settings, llm_mock)
        result = agent.check_compliance("Obra com geracao de 5 ton de residuos")
        assert isinstance(result, dict)
        assert "compliance_report" in result

    def test_generate_pgrs_returns_string(self, settings, llm_mock):
        from src.agents.compliance import ComplianceAgent
        agent = ComplianceAgent(settings, llm_mock)
        result = agent.generate_pgrs("Obra de 2000m2 em zona urbana")
        assert isinstance(result, str)

    def test_monitor_deadlines_returns_string(self, settings, llm_mock):
        from src.agents.compliance import ComplianceAgent
        agent = ComplianceAgent(settings, llm_mock)
        result = agent.monitor_deadlines("Licenca ambiental vence em 30 dias")
        assert isinstance(result, str)
