from typing import Dict, List

PLANS: List[Dict] = [
    {
        "id": "compliance_essencial",
        "name": "Compliance Essencial — NR-1 + LGPD",
        "price": 59000,
        "currency": "brl",
        "agents": ["nr1_psicossocial", "lgpd_operacional"],
        "trial_days": 15,
        "features": [
            "NR-1 Riscos Psicossociais (Portaria MTE 1.419/2024)",
            "LGPD Operacional (Lei 13.709/2018)",
            "Inventario FRPRT e plano de acao",
            "RoPA e mapeamento de dados",
            "Relatorios para fiscalizacao",
        ],
    },
    {
        "id": "regulatory_pro",
        "name": "Regulatory Pro — Obrigacoes Completas",
        "price": 149000,
        "currency": "brl",
        "agents": [
            "nr1_psicossocial", "tributario_cbs_ibs",
            "lgpd_operacional", "canal_denuncias",
            "igualdade_salarial", "compliance_anticorrupcao",
        ],
        "trial_days": 15,
        "features": [
            "Tudo do Compliance Essencial",
            "Canal de Denuncias (Lei 14.457/2022)",
            "Igualdade Salarial (Lei 14.611/2023)",
            "Compliance Anticorrupcao (Lei 12.846/2013)",
            "Tributario CBS/IBS (LC 214/2025)",
            "Relatorios para orgaos regulatorios",
        ],
    },
    {
        "id": "esg_carbon",
        "name": "ESG + Carbono PME",
        "price": 249000,
        "currency": "brl",
        "agents": [
            "esg_ifrs", "inventario_carbono",
            "escopo3_fornecedores",
        ],
        "trial_days": 15,
        "features": [
            "ESG IFRS S1/S2 (Res. CVM 193/2023)",
            "Inventario de Carbono Escopo 1/2 (GHG Protocol)",
            "Escopo 3 Fornecedores (SBCE + CBAM)",
            "Relatorios para SBCE e IFRS",
        ],
    },
    {
        "id": "aec_full",
        "name": "AEC Full — Engenharia e Construcao",
        "price": 468500,
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
            "Spec Analyst, Procurement, Inventory",
            "Logistics, Field Execution, BIM Coordinator",
            "Requirements Analyst, Engineering Assistant",
            "Work Synopsis, Photo Intelligence",
            "RFI Creation, Compliance Agent",
            "Suporte prioritario 24/7",
        ],
    },
    {
        "id": "microsoft_pack",
        "name": "Microsoft Compliance Pack",
        "price": 448200,
        "currency": "brl",
        "agents": [
            "regulatory_analyst", "compliance_pm",
            "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
        ],
        "trial_days": 15,
        "features": [
            "Regulatory Analyst (SharePoint/OneDrive)",
            "Compliance PM (Planner)",
            "Channel Agent Regulatorio (Teams)",
            "Knowledge Agent com RAG",
            "Facilitator Agent (reunioes)",
            "Dev Experience Agent (PRs e code review)",
            "Suporte prioritario 24/7",
        ],
    },
    {
        "id": "cross_sell_harmony",
        "name": "Cross-Sell Harmony — 3 Agentes",
        "price": 49000,
        "currency": "brl",
        "agents": [
            "onboarding_funcionarios",
        ],
        "trial_days": 15,
        "features": [
            "Onboarding de Funcionarios (admissao, contratos, acessos)",
            "Checklist de documentos e provisionamento",
            "Integracao com Teams e WhatsApp",
            "Relatorios de admissao",
        ],
    },
    {
        "id": "atendimento_plus",
        "name": "Atendimento Plus — Suporte PT-BR",
        "price": 39000,
        "currency": "brl",
        "agents": [
            "atendimento_cliente_ptbr",
        ],
        "trial_days": 15,
        "features": [
            "Atendimento ao Cliente PT-BR automatico",
            "Resolucao de tickets L1 via WhatsApp/Teams",
            "Categorizacao e escalonamento inteligente",
            "Relatorios de atendimento",
        ],
    },
    {
        "id": "conciliacao_pro",
        "name": "Conciliacao Pro — Fechamento Mensal",
        "price": 79000,
        "currency": "brl",
        "agents": [
            "conciliacao_financeira",
        ],
        "trial_days": 15,
        "features": [
            "Conciliacao de NFs com extratos bancarios",
            "Conciliacao de faturas de cartao",
            "Conciliacao de boletos emitidos vs pagos",
            "Relatorio executivo de fechamento mensal",
        ],
    },
    {
        "id": "full_suite",
        "name": "Full Suite — 30 Agentes",
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
            "regulatory_analyst", "compliance_pm",
            "channel_agent", "knowledge_agent",
            "facilitator_agent", "dev_experience",
            "onboarding_funcionarios",
            "atendimento_cliente_ptbr",
            "conciliacao_financeira",
        ],
        "trial_days": 15,
        "features": [
            "Todos os 30 agentes de IA",
            "AEC Core + Especializados + Conformidade",
            "Regulatorios + ESG + Carbono + Escopo 3",
            "Microsoft Pack completo (6 agentes M365)",
            "Cross-Sell: Onboarding, Atendimento, Conciliacao",
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
