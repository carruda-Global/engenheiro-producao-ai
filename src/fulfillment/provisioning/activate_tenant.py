import logging, uuid, json
from datetime import datetime
from src.database.supabase_client import SupabaseClient
from src.monetization.plans import get_plan_by_id

logger = logging.getLogger(__name__)

AGENT_IDS = {
    "#1": "spec_analyst", "#2": "procurement", "#3": "inventory", "#4": "logistics",
    "#5": "field_execution", "#6": "bim_coordinator", "#7": "requirements_analyst",
    "#8": "engineering_assistant", "#9": "work_synopsis", "#10": "photo_intelligence",
    "#11": "rfi_creation", "#12": "compliance",
    "#13": "nr1_psicossocial", "#14": "tributario_cbs_ibs", "#15": "lgpd_operacional",
    "#16": "esg_ifrs", "#17": "inventario_carbono", "#18": "escopo3_fornecedores",
    "#19": "canal_denuncias", "#20": "igualdade_salarial", "#21": "compliance_anticorrupcao",
    "#22": "regulatory_analyst", "#23": "compliance_pm", "#24": "channel_agent",
    "#25": "knowledge_agent", "#26": "facilitator_agent", "#27": "dev_experience",
    "N1": "onboarding_funcionarios", "N2": "atendimento_cliente_ptbr", "N3": "conciliacao_financeira",
    "#31": "dynamics_sales", "#32": "dynamics_finance", "#33": "dynamics_supply_chain",
    "#34": "dynamics_hr", "#35": "dynamics_cs", "#36": "powerbi_compliance",
    "#49": "master_orchestrator", "#50": "cross_platform_bridge",
    "#51": "regulatory_watch", "#52": "client_intelligence", "#53": "quality_critic",
    "#54": "meta_learning", "#55": "ecosystem_evolution", "#56": "federated_knowledge",
    "#57": "software_engineering", "#58": "sales_agent", "#59": "workforce_orchestrator",
}


class TenantActivator:
    def __init__(self, db: SupabaseClient):
        self.db = db

    def activate(self, customer_email: str, customer_name: str, plan_id: str, metadata: dict | None = None) -> dict:
        plan = get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        tenant_id = str(uuid.uuid4())
        api_key = f"aion_{uuid.uuid4().hex[:24]}"

        agent_list = plan.get("agents", [])
        if "all_71" in agent_list:
            agent_list = list(AGENT_IDS.keys())

        activated_agents = []
        for ref in agent_list:
            agent_id = AGENT_IDS.get(ref)
            if agent_id:
                config = {"tenant_id": tenant_id, "plan_id": plan_id, "status": "active", "activated_at": datetime.now().isoformat()}
                self.db.client.table("agent_activations").insert({"tenant_id": tenant_id, "agent_id": agent_id, "config": config}).execute()
                activated_agents.append(agent_id)

        tenant_data = {
            "id": tenant_id,
            "name": customer_name,
            "email": customer_email,
            "plan_id": plan_id,
            "plan_name": plan["name"],
            "api_key": api_key,
            "agents": activated_agents,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.db.client.table("tenants").insert(tenant_data).execute()

        logger.info(f"Tenant ativado: {tenant_id} | plano: {plan['name']} | agentes: {len(activated_agents)}")
        return tenant_data


class TenantsAPI:
    def __init__(self, db: SupabaseClient):
        self.db = db

    def get_tenant(self, tenant_id: str) -> dict | None:
        r = self.db.client.table("tenants").select("*").eq("id", tenant_id).execute()
        return r.data[0] if r.data else None

    def get_tenant_by_email(self, email: str) -> dict | None:
        r = self.db.client.table("tenants").select("*").eq("email", email).execute()
        return r.data[0] if r.data else None

    def get_tenant_agents(self, tenant_id: str) -> list:
        r = self.db.client.table("tenants").select("agents").eq("id", tenant_id).execute()
        return r.data[0].get("agents", []) if r.data else []

    def update_tenant_plan(self, tenant_id: str, plan_id: str) -> dict:
        plan = get_plan_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")
        self.db.client.table("tenants").update({"plan_id": plan_id, "plan_name": plan["name"]}).eq("id", tenant_id).execute()
        logger.info(f"Tenant {tenant_id} atualizado para plano {plan['name']}")
        return self.get_tenant(tenant_id)

    def deactivate_tenant(self, tenant_id: str):
        self.db.client.table("tenants").update({"status": "inactive"}).eq("id", tenant_id).execute()
        logger.info(f"Tenant {tenant_id} desativado")
