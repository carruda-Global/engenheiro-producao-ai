import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.mark.integration
class TestAPI:
    @pytest.fixture
    def client(self):
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def test_health_endpoint(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

    async def test_list_agents_endpoint(self, client):
        response = await client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data

    async def test_list_plans(self, client):
        response = await client.get("/api/v1/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 10

    async def test_get_plan_by_id(self, client):
        response = await client.get("/api/v1/subscriptions/plans/starter")
        assert response.status_code == 200
        assert response.json()["plan"]["id"] == "starter"

    async def test_get_plan_not_found(self, client):
        response = await client.get("/api/v1/subscriptions/plans/invalid")
        assert response.status_code == 404

    @patch("app.routers.agents.orchestrator")
    async def test_spec_analyst_no_api_key(self, mock_orch, client):
        spec_mock = MagicMock()
        spec_mock.analyze_document.return_value = {"agent": "spec_analyst", "analysis": "ok"}
        agent_map = {"spec_analyst": spec_mock}
        mock_orch.agents = agent_map

        response = await client.post(
            "/api/v1/agents/spec-analyst/analyze",
            json={"document": "Teste de documento"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "spec_analyst"
