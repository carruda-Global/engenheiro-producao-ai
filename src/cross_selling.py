import logging
from typing import Any

from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

AGENT_CHAIN = [
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
    "nr1_psicossocial",
    "tributario_cbs_ibs",
    "lgpd_operacional",
    "esg_ifrs",
    "inventario_carbono",
    "escopo3_fornecedores",
    "canal_denuncias",
    "igualdade_salarial",
    "compliance_anticorrupcao",
    "regulatory_analyst",
    "compliance_pm",
    "channel_agent",
    "knowledge_agent",
    "facilitator_agent",
    "dev_experience",
]

UPGRADE_PATH = {
    "starter": "professional",
    "professional": "enterprise",
    "enterprise": "full_suite",
}

COMPLIANCE_UPSELL_TARGETS = ["starter", "professional", "enterprise"]


def get_next_upgrade(current_plan_id: str) -> dict | None:
    next_id = UPGRADE_PATH.get(current_plan_id)
    if next_id:
        return get_plan(next_id)
    return None


def get_upsell_plans(current_plan_id: str) -> list[dict]:
    plans = []
    if current_plan_id in COMPLIANCE_UPSELL_TARGETS:
        compliance = get_plan("compliance_pack")
        if compliance:
            plans.append(compliance)
    next_up = get_next_upgrade(current_plan_id)
    if next_up:
        plans.append(next_up)
    if not plans:
        full = get_plan("full_suite")
        if full:
            plans.append(full)
    return plans


def get_agents_for_plan(plan_id: str) -> list[str]:
    plan = get_plan(plan_id)
    return plan["agents"] if plan else []


def get_missing_agents(current_agents: list[str], target_plan_id: str) -> list[str]:
    target_agents = get_agents_for_plan(target_plan_id)
    return [a for a in target_agents if a not in current_agents]


def estimate_monthly_savings(current_plan_id: str, target_plan_id: str) -> float:
    current = get_plan(current_plan_id)
    target = get_plan(target_plan_id)
    if not current or not target:
        return 0.0
    current_monthly = current["price"] / 100
    target_monthly = target["price"] / 100
    current_agents = len(current["agents"])
    target_agents = len(target["agents"])
    if current_agents == 0:
        return 0.0
    avg_cost_per_agent = current_monthly / current_agents
    hypothetical_cost = avg_cost_per_agent * target_agents
    savings = hypothetical_cost - target_monthly
    return max(0, savings)


def get_agent_name(agent_id: str) -> str:
    names = {
        "spec_analyst": "Spec Analyst",
        "procurement": "Procurement",
        "inventory": "Inventory",
        "logistics": "Logistics",
        "field_execution": "Field Execution",
        "bim_coordinator": "BIM Coordinator",
        "requirements_analyst": "Requirements Analyst",
        "engineering_assistant": "Engineering Assistant",
        "work_synopsis": "Work Synopsis",
        "photo_intelligence": "Photo Intelligence",
        "rfi_creation": "RFI Creation",
        "compliance": "Compliance Agent",
        "nr1_psicossocial": "NR-1 Psicossocial",
        "tributario_cbs_ibs": "Tributário CBS/IBS",
        "lgpd_operacional": "LGPD Operacional",
        "esg_ifrs": "ESG IFRS S1/S2",
        "inventario_carbono": "Inventário de Carbono",
        "escopo3_fornecedores": "Escopo 3 Fornecedores",
        "canal_denuncias": "Canal de Denúncias",
        "igualdade_salarial": "Igualdade Salarial",
        "compliance_anticorrupcao": "Compliance Anticorrupção",
        "regulatory_analyst": "Regulatory Analyst",
        "compliance_pm": "Compliance PM",
        "channel_agent": "Channel Agent Regulatório",
        "knowledge_agent": "Knowledge Agent",
        "facilitator_agent": "Facilitator Agent",
        "dev_experience": "Dev Experience Agent",
    }
    return names.get(agent_id, agent_id)
