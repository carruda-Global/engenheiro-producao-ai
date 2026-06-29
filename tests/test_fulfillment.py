import pytest
from unittest.mock import MagicMock, patch
from src.fulfillment.provisioning.activate_tenant import TenantActivator, TenantsAPI


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    db.client.table.return_value.insert.return_value.execute.return_value.data = [{}]
    return db


class TestTenantActivator:
    def test_activate_starter_plan(self, mock_db):
        activator = TenantActivator(mock_db)
        result = activator.activate("teste@email.com", "Empresa Teste", "starter")
        assert result["email"] == "teste@email.com"
        assert result["plan_id"] == "starter"
        assert "api_key" in result
        assert result["api_key"].startswith("aion_")

    def test_activate_regulatory_pro(self, mock_db):
        activator = TenantActivator(mock_db)
        result = activator.activate("cliente@email.com", "Cliente ABC", "regulatory_pro")
        assert result["plan_id"] == "regulatory_pro"
        assert len(result["agents"]) >= 5

    def test_invalid_plan(self, mock_db):
        activator = TenantActivator(mock_db)
        with pytest.raises(ValueError, match="Plano invalido"):
            activator.activate("teste@email.com", "Teste", "plano_inexistente")


class TestTenantsAPI:
    def test_get_tenant_not_found(self, mock_db):
        api = TenantsAPI(mock_db)
        result = api.get_tenant("inexistente")
        assert result is None

    def test_get_tenant_by_email_not_found(self, mock_db):
        api = TenantsAPI(mock_db)
        result = api.get_tenant_by_email("nao@existe.com")
        assert result is None


class TestFulfillmentFlow:
    def test_full_flow_starter(self, mock_db):
        activator = TenantActivator(mock_db)
        tenant = activator.activate("empresa@teste.com", "Empresa Ltda", "starter")
        assert tenant["status"] == "active"
        assert len(tenant["agents"]) == 1
        assert tenant["plan_name"] == "AEC Starter"

    def test_full_flow_full_suite(self, mock_db):
        activator = TenantActivator(mock_db)
        tenant = activator.activate("empresa@teste.com", "Empresa Ltda", "full_suite")
        assert tenant["status"] == "active"
        assert len(tenant["agents"]) > 50

    def test_esg_carbon_plan(self, mock_db):
        activator = TenantActivator(mock_db)
        tenant = activator.activate("esg@empresa.com", "ESG Ltda", "esg_carbono")
        assert len(tenant["agents"]) == 3
