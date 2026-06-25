from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Settings
from src.core.orchestrator import HMASOrchestrator
from src.monitoring.agent_dashboard import AgentDashboard
from src.security.circuit_breaker import CircuitBreaker

from app.routers.salesforce_marketplace import router as salesforce_router
from app.routers.subscriptions import router as subscriptions_router
from app.routers.health import router as health_router
from app.routers.aip_security import router as aip_router
from app.routers.microsoft_marketplace import router as microsoft_router
from app.routers.cross_selling import router as cross_selling_router

settings = Settings()

app = FastAPI(
    title="H-MAS EcoSystem AEC + Regulatory",
    description="27 Agentes de IA Hierárquicos para Engenharia de Produção",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = HMASOrchestrator(tenant_id="default")
dashboard = AgentDashboard()
circuit_breaker = CircuitBreaker(threshold=5, reset_seconds=60)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    logger.info("Inicializando H-MAS com 30 agentes...")
    await orchestrator.initialize()
    logger.info("Sistema pronto. 30/30 agentes ativos.")


app.include_router(salesforce_router, prefix="/salesforce", tags=["salesforce"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(aip_router)
app.include_router(microsoft_router, prefix="/microsoft", tags=["microsoft"])
app.include_router(cross_selling_router, prefix="/api/cross-sell", tags=["cross-sell"])


@app.get("/")
async def root():
    return {
        "service": "H-MAS EcoSystem AEC + Regulatory",
        "version": "3.0.0",
        "status": "operational",
        "agents_total": 30,
        "clusters": ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft"],
    }


@app.get("/api/status/{tenant_id}")
async def get_status(tenant_id: str):
    return dashboard.get_agent_status(tenant_id)


@app.post("/api/agents/initialize")
async def initialize_agents(data: dict):
    tenant = data.get("tenant", "default")
    clusters = data.get("clusters", ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft"])
    orchestrator.tenant_id = tenant
    await orchestrator.initialize()
    return {
        "status": "initialized",
        "tenant": tenant,
        "clusters": clusters,
        "agents_total": len(orchestrator.agents),
    }


@app.post("/api/agents/execute")
async def execute_task(data: dict):
    result = await orchestrator.execute_task(data, user_id=data.get("user_id", "anonymous"))
    return result


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
