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
        "id": "dynamics_pack",
        "name": "Microsoft Dynamics Pack — 6 Agentes",
        "price": 399000,
        "currency": "brl",
        "agents": [
            "dynamics_sales", "dynamics_finance",
            "dynamics_supply_chain", "dynamics_hr",
            "dynamics_customer_service", "powerbi_compliance",
        ],
        "trial_days": 15,
        "features": [
            "Dynamics Sales Agent",
            "Dynamics Finance Agent",
            "Dynamics Supply Chain Agent",
            "Dynamics HR Agent",
            "Dynamics Customer Service Agent",
            "Power BI Compliance Dashboard",
        ],
    },
    {
        "id": "agentforce_pack",
        "name": "Salesforce Agentforce Pack — 5 Agentes",
        "price": 369000,
        "currency": "brl",
        "agents": [
            "agentforce_sdr", "agentforce_field_service",
            "agentforce_contracts", "agentforce_revenue",
            "agentforce_sustainability",
        ],
        "trial_days": 15,
        "features": [
            "Agentforce SDR Agent",
            "Agentforce Field Service Agent",
            "Agentforce Contract Intelligence",
            "Agentforce Revenue Intelligence",
            "Agentforce Sustainability Agent",
        ],
    },
    {
        "id": "oracle_pack",
        "name": "Oracle Fusion Pack — 4 Agentes",
        "price": 399000,
        "currency": "brl",
        "agents": [
            "oracle_erp_compliance", "oracle_hcm_regulatory",
            "oracle_supply_chain_esg", "oracle_cx_sales",
        ],
        "trial_days": 15,
        "features": [
            "Oracle ERP Compliance Agent",
            "Oracle HCM Regulatory Agent",
            "Oracle Supply Chain ESG Agent",
            "Oracle CX Sales Intelligence Agent",
        ],
    },
    {
        "id": "sap_pack",
        "name": "SAP Integration Pack — 3 Agentes",
        "price": 429000,
        "currency": "brl",
        "agents": [
            "sap_compliance_bridge", "sap_predictive_maintenance",
            "sap_cbam_export",
        ],
        "trial_days": 15,
        "features": [
            "SAP Joule Compliance Bridge Agent",
            "SAP Predictive Maintenance Agent",
            "SAP CBAM Export Compliance Agent",
            "Integracao com SAP S/4HANA e BTP",
        ],
    },
    {
        "id": "erp_full_bridge",
        "name": "ERP Full Bridge — 18 Agentes",
        "price": 1299000,
        "currency": "brl",
        "agents": [
            "dynamics_sales", "dynamics_finance", "dynamics_supply_chain",
            "dynamics_hr", "dynamics_customer_service", "powerbi_compliance",
            "agentforce_sdr", "agentforce_field_service", "agentforce_contracts",
            "agentforce_revenue", "agentforce_sustainability",
            "oracle_erp_compliance", "oracle_hcm_regulatory",
            "oracle_supply_chain_esg", "oracle_cx_sales",
            "sap_compliance_bridge", "sap_predictive_maintenance", "sap_cbam_export",
        ],
        "trial_days": 15,
        "features": [
            "18 agentes ERP (Dynamics + Agentforce + Oracle + SAP)",
            "Cross-Platform Bridge incluso",
            "Suporte prioritario 24/7",
            "Onboarding dedicado",
        ],
    },
    {
        "id": "full_suite_56",
        "name": "Full Suite — 56 Agentes",
        "price": 1999700,
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
            "dynamics_sales", "dynamics_finance",
            "dynamics_supply_chain", "dynamics_hr",
            "dynamics_customer_service", "powerbi_compliance",
            "agentforce_sdr", "agentforce_field_service",
            "agentforce_contracts", "agentforce_revenue",
            "agentforce_sustainability",
            "oracle_erp_compliance", "oracle_hcm_regulatory",
            "oracle_supply_chain_esg", "oracle_cx_sales",
            "sap_compliance_bridge", "sap_predictive_maintenance",
            "sap_cbam_export",
            "master_orchestrator", "cross_platform_bridge",
            "regulatory_watch", "client_intelligence",
            "quality_critic", "meta_learning",
            "ecosystem_evolution", "federated_knowledge",
        ],
        "trial_days": 15,
        "features": [
            "Todos os 56 agentes de IA",
            "AEC Core + Especializados + Conformidade",
            "Regulatorios + ESG + Carbono + Escopo 3",
            "Microsoft Pack (6 agentes M365)",
            "Dynamics, Agentforce, Oracle, SAP",
            "Master Orchestrator + Quality Critic",
            "Regulatory Watch + Client Intelligence",
            "Meta-Learning + Ecosystem Evolution",
            "Cross-Platform Bridge incluso",
            "Suporte prioritario 24/7",
        ],
    },
]

def get_plan(plan_id: str) -> dict | None:
    for plan in PLANS:
        if plan["id"] == plan_id:
            return plan
    return None


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
