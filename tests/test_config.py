import pytest
from src.config import Settings


@pytest.mark.unit
class TestSettings:
    def test_settings_loads_config(self, settings):
        assert settings.deepseek_model == "deepseek-v4-flash"
        assert settings.deepseek_temperature == 0.3
        assert settings.deepseek_max_tokens == 16384

    def test_settings_validate_missing_key(self, settings):
        settings.deepseek_api_key = ""
        errors = settings.validate()
        assert len(errors) > 0

    def test_settings_validate_ok(self, settings):
        settings.deepseek_api_key = "sk-test"
        errors = settings.validate()
        assert len(errors) == 0

    def test_agents_config_loaded(self, settings):
        assert "spec_analyst" in settings.agents_config
        assert settings.agents_config["spec_analyst"]["enabled"] is True

    def test_plans_config_loaded(self, settings):
        assert "starter" in settings.plans_config
        assert settings.plans_config["starter"]["amount_cents"] == 99700
