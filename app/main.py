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
    logger.warning("Configuracao parcial no startup: %s", e)
    settings = None

app = FastAPI(
    title="H-MAS EcoSystem AEC + Regulatory",
    description="59 Agentes de IA Hierárquicos para Engenharia de Produção",
    version="3.0.0",
)

cors_origins = ["*"] if settings.app_env != "production" else [settings.base_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False if cors_origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = HMASOrchestrator(settings)
dashboard = AgentDashboard()
circuit_breaker = CircuitBreaker(threshold=5, reset_seconds=60)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    await init_pool()
    await init_producer()
    logger.info("Inicializando H-MAS com 59 agentes...")
    await orchestrator.initialize()
    logger.info("Sistema pronto. 59/59 agentes ativos.")


@app.on_event("shutdown")
async def shutdown():
    await close_producer()
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


@app.get("/")
async def root():
    return {
        "service": "H-MAS EcoSystem AEC + Regulatory",
        "version": "3.0.0",
        "status": "operational",
        "agents_total": len(orchestrator.agents),
        "clusters": ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft", "cross_sell", "dynamics", "agentforce", "oracle", "sap", "coordination", "intelligence", "tech", "self_improvement"],
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
    return {"id": server_id, "name": f"Ecosystem {server_id.title()} MCP", "description": f"MCP server for {server_id} agents", "tools": [{"name": t} for t in server["tools"]]}


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
