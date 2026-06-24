from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Settings
from src.core.orchestrator import HMASOrchestrator
from src.monitoring.agent_dashboard import AgentDashboard
from src.security.circuit_breaker import CircuitBreaker

settings = Settings()

app = FastAPI(
    title="H-MAS EcoSystem AEC + Regulatory",
    description="27 Agentes de IA Hierárquicos para Engenharia de Produção",
    version="3.0.0",
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
    logger.info("Inicializando H-MAS com 27 agentes...")
    await orchestrator.initialize()
    logger.info("Sistema pronto. 27/27 agentes ativos.")


@app.get("/")
async def root():
    return {
        "service": "H-MAS EcoSystem AEC + Regulatory",
        "version": "3.0.0",
        "status": "operational",
        "agents_total": 27,
        "clusters": ["production", "logistics", "quality"],
    }


@app.get("/api/status/{tenant_id}")
async def get_status(tenant_id: str):
    return dashboard.get_agent_status(tenant_id)


@app.post("/api/agents/initialize")
async def initialize_agents(data: dict):
    tenant = data.get("tenant", "default")
    clusters = data.get("clusters", ["production", "logistics", "quality"])
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
    statuses = {
        agent_id: {
            "status": agent.status,
            "success_rate": agent.success_rate,
            "total_tasks": agent.total_tasks,
            "avg_response_time": agent.avg_response_time,
        }
        for agent_id, agent in orchestrator.agents.items()
    }
    return {
        "total_agents": len(statuses),
        "agents": statuses,
    }
