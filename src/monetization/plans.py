from typing import Dict, List

PLANS: List[Dict] = [
    {
        "id": "starter",
        "name": "Starter - Spec Analyst",
        "price": 99700,
        "currency": "brl",
        "agents": ["spec_analyst"],
        "trial_days": 15,
        "features": [
            "Analise de ate 50 documentos/mes",
            "Extrai requisitos tecnicos",
            "Sinaliza nao-conformidades",
        ],
    },
    {
        "id": "professional",
        "name": "Professional - Spec Analyst + Procurement",
        "price": 159700,
        "currency": "brl",
        "agents": ["spec_analyst", "procurement"],
        "trial_days": 15,
        "features": [
            "Analise de documentos ilimitada",
            "Compras e pedidos automatizados",
            "Comparacao de cotacoes",
        ],
    },
    {
        "id": "enterprise",
        "name": "Enterprise - 4 Agentes",
        "price": 299700,
        "currency": "brl",
        "agents": ["spec_analyst", "procurement", "inventory", "logistics"],
        "trial_days": 15,
        "features": [
            "Todos os recursos do Professional",
            "Monitoramento de estoque em tempo real",
            "Logistica e atendimento",
        ],
    },
    {
        "id": "full_suite",
        "name": "Full Suite - Todos os 5 Agentes",
        "price": 350000,
        "currency": "brl",
        "agents": [
            "spec_analyst",
            "procurement",
            "inventory",
            "logistics",
            "field_execution",
        ],
        "trial_days": 15,
        "features": [
            "Todos os 5 agentes de IA",
            "Cross-selling automatico",
            "Execucao em campo com RA",
            "Suporte prioritario 24/7",
        ],
    },
]


def get_plan(plan_id: str) -> dict | None:
    for plan in PLANS:
        if plan["id"] == plan_id:
            return plan
    return None


def get_plan_for_agents(agent_ids: list[str]) -> dict | None:
    candidates = [
        plan for plan in PLANS
        if all(a in plan["agents"] for a in agent_ids)
    ]
    return min(candidates, key=lambda p: len(p["agents"])) if candidates else None
