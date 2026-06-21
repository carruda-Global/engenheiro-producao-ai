import pytest
from src.monetization.plans import PLANS, get_plan, get_plan_for_agents


@pytest.mark.unit
class TestPlans:
    def test_plans_have_correct_structure(self):
        assert len(PLANS) == 4
        for plan in PLANS:
            assert "id" in plan
            assert "name" in plan
            assert "price" in plan
            assert "currency" in plan
            assert "agents" in plan
            assert "features" in plan

    def test_starter_plan_price(self):
        plan = get_plan("starter")
        assert plan is not None
        assert plan["price"] == 99700

    def test_full_suite_has_all_agents(self):
        plan = get_plan("full_suite")
        assert plan is not None
        assert len(plan["agents"]) == 5

    def test_get_plan_invalid_returns_none(self):
        plan = get_plan("invalid_plan")
        assert plan is None

    def test_get_plan_for_agents_matches_correctly(self):
        plan = get_plan_for_agents(["spec_analyst"])
        assert plan is not None
        assert plan["id"] == "starter"

    def test_get_plan_for_agents_full_suite(self):
        all_agents = [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
        ]
        plan = get_plan_for_agents(all_agents)
        assert plan is not None
        assert plan["id"] == "full_suite"
