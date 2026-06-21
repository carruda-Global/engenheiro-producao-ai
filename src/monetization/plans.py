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
        "name": "Professional - 3 Agentes",
        "price": 239100,
        "currency": "brl",
        "agents": ["spec_analyst", "procurement", "inventory"],
        "trial_days": 15,
        "features": [
            "Analise de documentos ilimitada",
            "Compras e pedidos automatizados",
            "Monitoramento de estoque",
        ],
    },
    {
        "id": "enterprise",
        "name": "Enterprise - 5 Agentes",
        "price": 468500,
        "currency": "brl",
        "agents": [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
        ],
        "trial_days": 15,
        "features": [
            "Todos os recursos do Professional",
            "Logistica e rastreamento de entregas",
            "Instrucoes de campo com IA",
            "Cross-selling automatico",
        ],
    },
    {
        "id": "full_suite",
        "name": "Full Suite - 12 Agentes",
        "price": 949700,
        "currency": "brl",
        "agents": [
            "spec_analyst", "procurement", "inventory",
            "logistics", "field_execution",
            "bim_coordinator", "requirements_analyst",
            "engineering_assistant", "work_synopsis",
            "photo_intelligence", "rfi_creation", "compliance",
        ],
        "trial_days": 15,
        "features": [
            "Todos os 12 agentes de IA",
            "BIM Coordinator com clash detection",
            "Photo Intelligence e analise visual",
            "RFI Creation automatizada",
            "Compliance Agent com PGRS/PGRSS",
            "Suporte prioritario 24/7",
        ],
    },
    {
        "id": "compliance_pack",
        "name": "Compliance Pack - PGRS/PGRSS",
        "price": 239100,
        "currency": "brl",
        "agents": ["photo_intelligence", "rfi_creation", "compliance"],
        "trial_days": 15,
        "features": [
            "Photo Intelligence para obras",
            "Criacao automatica de RFIs",
            "Gestao de conformidade PGRS/PGRSS",
            "Monitoramento de prazos legais",
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
