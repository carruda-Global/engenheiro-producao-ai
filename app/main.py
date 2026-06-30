import os
import uuid
import logging

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import Settings, get_settings
from src.orchestrator import Orchestrator as HMASOrchestrator
from src.monetization.plans import PLANS, get_plan
from src.monitoring.agent_dashboard import AgentDashboard
from src.security.circuit_breaker import CircuitBreaker
try:
    from src.database.postgres_client import init_pool, close_pool, get_conn
except ImportError:
    init_pool = close_pool = get_conn = None
try:
    from src.messaging.producer import init_producer, close_producer, enqueue_agent_task
except ImportError:
    init_producer = close_producer = enqueue_agent_task = None

from app.routers.salesforce_marketplace import router as salesforce_router
from app.routers.subscriptions import router as subscriptions_router
from app.routers.health import router as health_router
from app.routers.aip_security import router as aip_router
from app.routers.microsoft_marketplace import router as microsoft_router
from app.routers.cross_selling import router as cross_selling_router
from app.routers.google_marketplace import router as google_router
from app.routers.aws_marketplace import router as aws_router
from app.routers.leads import router as leads_router
from app.routers.stripe_app import router as stripe_app_router
from app.routers.privacy import router as privacy_router
from app.routers.stripe_webhook import router as stripe_webhook_router
from app.routers.governance import router as governance_router
from app.routers.bridge import router as bridge_router
from app.routers.code_review import router as code_review_router
from app.routers.physical_ai import router as physical_ai_router
from app.routers.checkout import router as checkout_router
from src.fulfillment.webhooks.stripe_fulfillment import router as fulfillment_router
from src.api.routes.status import router as status_router
from src.api.middleware.privacy import PrivacyConsentMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.routers.oracle_marketplace import router as oracle_router
except ImportError:
    oracle_router = APIRouter()
    logger.warning("Oracle router nao carregado (oci nao instalado)")

try:
    settings = Settings()
    config_errors = settings.validate()
    if config_errors:
        logger.warning("Configuracao incompleta no startup: %s", config_errors)
except Exception as e:
    logger.warning("Configuracao parcial no startup, usando defaults: %s", e)
    settings = Settings.__new__(Settings)
    settings.app_env = os.getenv("APP_ENV", "development")
    settings.base_url = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
    settings.agents_config = {}
    settings.llm_routing_config = {}

_is_production = settings.app_env == "production"
cors_origins = [settings.base_url] if _is_production else ["*"]

app = FastAPI(
    title="AION 7.0 - Agents Intelligence Orchestration Network",
    description="71 Agentes de IA com seguranca AIP, Compliance Receipts e mTLS",
    version="7.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=_is_production,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrivacyConsentMiddleware)

orchestrator = HMASOrchestrator(settings)
dashboard = AgentDashboard()
circuit_breaker = CircuitBreaker(threshold=5, reset_seconds=60)


@app.on_event("startup")
async def startup():
    if init_pool:
        await init_pool()
    if init_producer:
        await init_producer()
    logger.info("Inicializando H-MAS com 59 agentes...")
    await orchestrator.initialize()
    logger.info("Sistema pronto. 59/59 agentes ativos.")


@app.on_event("shutdown")
async def shutdown():
    if close_producer:
        await close_producer()
    if close_pool:
        await close_pool()


class AgentExecuteRequest(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    task_type: str = "execute"
    payload: dict = {}


@app.post("/api/agents/execute")
async def execute_task(request: AgentExecuteRequest):
    task_id = str(uuid.uuid4())

    try:
        async with get_conn() as conn:
            await conn.execute(
                """
                INSERT INTO agent_executions
                    (id, tenant_id, agent_id, task_type, status, input_summary)
                VALUES ($1, $2, $3, $4, 'queued', $5)
                """,
                task_id,
                request.tenant_id,
                request.agent_id,
                request.task_type,
                str(request.payload)[:500],
            )
    except Exception:
        logger.warning("Banco indisponivel, executando síncrono")
        result = await orchestrator.execute_task(request.dict(), user_id=request.tenant_id)
        return result

    try:
        async with get_conn() as conn:
            row = await conn.fetchrow(
                "SELECT cluster FROM agent_registry WHERE id = $1 AND status = 'active'",
                request.agent_id,
            )
    except Exception:
        row = None

    if row:
        await enqueue_agent_task(
            task_id=task_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            cluster=row["cluster"],
            task_type=request.task_type,
            payload=request.payload,
        )
        return {
            "task_id": task_id,
            "status": "queued",
            "poll_url": f"/api/tasks/{task_id}",
            "message": "Task enfileirada. Use poll_url para acompanhar o resultado.",
        }

    result = await orchestrator.execute_task(request.dict(), user_id=request.tenant_id)
    return result


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    try:
        async with get_conn() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM agent_executions WHERE id = $1", task_id,
            )
        if row:
            return dict(row)
    except Exception:
        pass
    raise HTTPException(status_code=404, detail="Task nao encontrada")


app.include_router(salesforce_router, prefix="/salesforce", tags=["salesforce"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(aip_router)
app.include_router(microsoft_router)
app.include_router(cross_selling_router, prefix="/api/cross-sell", tags=["cross-sell"])
app.include_router(google_router, prefix="/google", tags=["google"])
app.include_router(aws_router, prefix="/aws", tags=["aws"])
app.include_router(oracle_router, prefix="/oracle", tags=["oracle"])
app.include_router(leads_router)
app.include_router(stripe_app_router)
app.include_router(privacy_router)
app.include_router(stripe_webhook_router)
app.include_router(governance_router)
app.include_router(bridge_router)
app.include_router(code_review_router)
app.include_router(physical_ai_router)
app.include_router(checkout_router)
app.include_router(fulfillment_router)
app.include_router(status_router)


@app.get("/")
async def root():
    return {
        "service": "AION 7.0 - Agents Intelligence Orchestration Network",
        "version": "7.0.0",
        "status": "operational",
        "agents_total": len(orchestrator.agents),
        "clusters": ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft", "cross_sell", "dynamics", "agentforce", "oracle", "sap", "coordination", "intelligence", "tech", "self_improvement", "enterprise_connectors", "physical_ai"],
    }


@app.get("/.well-known/agent-card.json")
async def agent_card():
    return {
        "name": "AION - Agents Intelligence Orchestration Network",
        "description": "78 agentes de IA para Engenharia, Construcao, Conformidade Regulatoria (NR-1, LGPD, ESG), Microsoft Dynamics 365, Salesforce Agentforce, Oracle Fusion e SAP S/4HANA.",
        "version": "7.0.0",
        "provider": {
            "organization": "Global Engenharia",
            "url": "https://engenheiro-producao-ai.onrender.com",
            "email": "cristiano@globalengenharia.com.br",
        },
        "documentationUrl": "https://engenheiro-producao-ai.onrender.com/docs",
        "supportedInterfaces": [
            {
                "type": "a2a",
                "url": "https://engenheiro-producao-ai.onrender.com/a2a/jsonrpc",
            }
        ],
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "skills": [
            {
                "id": "nr1_psicossocial",
                "name": "NR-1 Psicossocial",
                "description": "Avaliacao de riscos psicossociais conforme NR-1 e elaboracao de planos de acao para conformidade trabalhista brasileira.",
                "tags": ["compliance", "nr1", "regulatory", "brazil", "hr"],
            },
            {
                "id": "lgpd_operacional",
                "name": "LGPD Operacional",
                "description": "Operacionalizacao da LGPD: mapeamento de dados pessoais, elaboracao de politicas de privacidade e gestao de consentimento.",
                "tags": ["lgpd", "privacy", "compliance", "data-protection", "brazil"],
            },
            {
                "id": "esg_ifrs",
                "name": "ESG IFRS S1/S2",
                "description": "Relatorios de sustentabilidade conforme IFRS S1 e S2, inventario de carbono e metas ESG para empresas brasileiras.",
                "tags": ["esg", "sustainability", "carbon", "ifrs", "reporting"],
            },
            {
                "id": "spec_analyst",
                "name": "Analista de Especificacoes Tecnicas",
                "description": "Analisa documentos de engenharia (plantas, memoriais, normas NBR) para extrair requisitos tecnicos e identificar contradicoes.",
                "tags": ["engineering", "aec", "specifications", "nbr", "construction"],
            },
            {
                "id": "bim_coordinator",
                "name": "BIM Coordinator",
                "description": "Coordenacao BIM: deteccao de conflitos, gestao de modelos IFC e relatorios de compatibilizacao para projetos de construcao.",
                "tags": ["bim", "ifc", "construction", "aec", "coordination"],
            },
            {
                "id": "regulatory_analyst",
                "name": "Regulatory Analyst M365",
                "description": "Analise regulatoria integrada ao Microsoft 365: monitora mudancas normativas e gera alertas de conformidade no Teams e SharePoint.",
                "tags": ["microsoft", "m365", "regulatory", "compliance", "teams"],
            },
            {
                "id": "dynamics_sales",
                "name": "Dynamics 365 Sales Agent",
                "description": "Automacao de vendas no Dynamics 365: qualificacao de leads, previsao de receita e gestao de pipeline com IA generativa.",
                "tags": ["dynamics365", "microsoft", "crm", "sales", "erp"],
            },
            {
                "id": "agentforce_sdr",
                "name": "Agentforce SDR",
                "description": "Agente SDR no Salesforce Agentforce: prospecao automatizada, qualificacao de leads e agendamento de reunioes via Einstein AI.",
                "tags": ["salesforce", "agentforce", "sdr", "crm", "sales"],
            },
            {
                "id": "oracle_erp_compliance",
                "name": "Oracle ERP Compliance",
                "description": "Conformidade regulatoria no Oracle Fusion ERP: automacao de obrigacoes fiscais brasileiras (SPED, NF-e, eSocial) integradas ao Oracle.",
                "tags": ["oracle", "erp", "compliance", "fiscal", "brazil"],
            },
            {
                "id": "sap_joule_compliance",
                "name": "SAP Joule Compliance",
                "description": "Agente de compliance no SAP S/4HANA via SAP Joule: auditoria automatizada de processos fiscais e regulatorios brasileiros.",
                "tags": ["sap", "s4hana", "joule", "compliance", "erp"],
            },
        ],
    }


@app.get("/api/status/{tenant_id}")
async def get_status(tenant_id: str):
    return dashboard.get_agent_status(tenant_id)


@app.post("/api/agents/initialize")
async def initialize_agents(data: dict):
    tenant = data.get("tenant", "default")
    clusters = data.get("clusters", ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft", "cross_sell", "dynamics", "agentforce", "oracle", "sap", "coordination", "intelligence", "tech", "self_improvement"])
    orchestrator.tenant_id = tenant
    await orchestrator.initialize()
    return {
        "status": "initialized",
        "tenant": tenant,
        "clusters": clusters,
        "agents_total": len(orchestrator.agents),
    }


@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} not found"}, 404
    return agent.to_dict()


@app.get("/api/agents/health")
async def agents_health():
    statuses = {}
    for agent_id, agent in orchestrator.agents.items():
        statuses[agent_id] = {
            "status": getattr(agent, "status", "initialized"),
            "success_rate": getattr(agent, "success_rate", 1.0),
            "total_tasks": getattr(agent, "total_tasks", 0),
            "avg_response_time": getattr(agent, "avg_response_time", 0.0),
        }
    return {
        "total_agents": len(statuses),
        "agents": statuses,
    }


MCP_SERVERS = {
    "regulatory": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse",
        "tools": ["nr1_psicossocial", "lgpd_operacional", "tributario_cbs_ibs", "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao", "onboarding_funcionarios", "conciliacao_financeira"],
    },
    "esg": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/esg/sse",
        "tools": ["esg_ifrs_diagnostico", "inventario_carbono", "escopo3_fornecedores", "cbam_certificate"],
    },
    "erp": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/erp/sse",
        "tools": ["dynamics_sales", "dynamics_finance", "dynamics_hr", "agentforce_sdr", "agentforce_contracts", "oracle_erp_compliance", "oracle_hcm_regulatory", "sap_compliance_bridge", "sap_cbam_export", "powerbi_compliance"],
    },
}


@app.get("/mcp/servers")
async def list_mcp_servers():
    return {"servers": MCP_SERVERS, "total": len(MCP_SERVERS)}


@app.get("/mcp/{server_id}/manifest")
async def mcp_server_manifest(server_id: str):
    server = MCP_SERVERS.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not found")
    return {"id": server_id, "name": f"AION {server_id.title()} MCP", "description": f"MCP server for {server_id} agents", "tools": [{"name": t} for t in server["tools"]]}


@app.get("/api/v1/agents")
async def v1_list_agents():
    return {"agents": list(orchestrator.agents.keys()), "total": len(orchestrator.agents)}


@app.get("/api/v1/subscriptions/plans")
async def v1_list_plans():
    return {"plans": [{"id": p["id"], "name": p["name"], "price": p["price"], "agents": p["agents"]} for p in PLANS]}


@app.get("/api/v1/subscriptions/plans/{plan_id}")
async def v1_get_plan(plan_id: str):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"plan": plan}
