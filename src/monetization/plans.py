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
        "name": "Full Suite - 21 Agentes",
        "price": 949700,
        "currency": "brl",
        "agents": [
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
        ],
        "trial_days": 15,
        "features": [
            "Todos os 21 agentes de IA",
            "BIM Coordinator com clash detection",
            "Photo Intelligence e analise visual",
            "RFI Creation automatizada",
            "Compliance Agent com PGRS/PGRSS",
            "NR-1 Psicossocial completo",
            "Tributario CBS/IBS",
            "LGPD Operacional",
            "ESG IFRS S1/S2",
            "Inventario de Carbono Escopo 1/2",
            "Escopo 3 Fornecedores",
            "Canal de Denuncias",
            "Igualdade Salarial",
            "Compliance Anticorrupcao",
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
    {
        "id": "regulatory_starter",
        "name": "Regulatory Starter - NR-1 + LGPD",
        "price": 59000,
        "currency": "brl",
        "agents": ["nr1_psicossocial", "lgpd_operacional"],
        "trial_days": 15,
        "features": [
            "NR-1 Riscos Psicossociais",
            "LGPD Operacional",
            "Inventario e planos de acao",
            "Relatorios para fiscalizacao",
        ],
    },
    {
        "id": "regulatory_professional",
        "name": "Regulatory Professional - 5 Agentes",
        "price": 149000,
        "currency": "brl",
        "agents": [
            "nr1_psicossocial", "lgpd_operacional",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ],
        "trial_days": 15,
        "features": [
            "NR-1 Riscos Psicossociais",
            "LGPD Operacional",
            "Canal de Denuncias",
            "Igualdade Salarial",
            "Compliance Anticorrupcao",
            "Relatorios para orgaos regulatorios",
        ],
    },
    {
        "id": "regulatory_full",
        "name": "Regulatory Full - 9 Agentes",
        "price": 349000,
        "currency": "brl",
        "agents": [
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "esg_ifrs",
            "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial",
            "compliance_anticorrupcao",
        ],
        "trial_days": 15,
        "features": [
            "Todos os 9 agentes regulatorios",
            "Tributario CBS/IBS",
            "ESG IFRS S1/S2",
            "Inventario de Carbono Escopo 1 e 2",
            "Escopo 3 Fornecedores",
            "Dashboards de conformidade",
            "Suporte prioritario 24/7",
        ],
    },
    {
        "id": "esg_carbon_pack",
        "name": "ESG + Carbono",
        "price": 249000,
        "currency": "brl",
        "agents": [
            "esg_ifrs", "inventario_carbono",
            "escopo3_fornecedores",
        ],
        "trial_days": 15,
        "features": [
            "ESG IFRS S1/S2",
            "Inventario de Carbono Escopo 1/2",
            "Escopo 3 Fornecedores",
            "Relatorios para SBCE e IFRS",
        ],
    },
    {
        "id": "microsoft_pack",
        "name": "Microsoft Pack - 6 Agentes",
        "price": 448200,
        "currency": "brl",
        "agents": [
            "regulatory_analyst", "compliance_pm",
            "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
        ],
        "trial_days": 15,
        "features": [
            "Regulatory Analyst (R$ 997/mes)",
            "Compliance PM (R$ 797/mes)",
            "Channel Agent Regulatorio (R$ 597/mes)",
            "Knowledge Agent (R$ 697/mes)",
            "Facilitator Agent (R$ 497/mes)",
            "Dev Experience Agent (R$ 897/mes)",
            "Integracao com SharePoint e OneDrive",
            "Monitoramento de canais Teams",
            "Automacao de PRs e code reviews",
            "Indexacao de documentos com RAG",
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
