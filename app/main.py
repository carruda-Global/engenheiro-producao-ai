from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    acp_checkout, agents, aws_marketplace, cross_selling,
    google_marketplace, health, oracle_marketplace, pgrs, subscriptions,
)
from src.config import Settings
from src.a2a_bridge import setup_a2a_routes

settings = Settings()

app = FastAPI(
    title="EcoSystem AEC",
    description="12 Agentes de IA Integrados para Arquitetura, Engenharia e Construcao",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
app.include_router(acp_checkout.router, prefix="/api/v1/acp", tags=["agentic-commerce"])
app.include_router(aws_marketplace.router, prefix="/api/v1/aws-marketplace", tags=["aws-marketplace"])
app.include_router(oracle_marketplace.router, prefix="/api/v1/oracle-marketplace", tags=["oracle-marketplace"])
app.include_router(google_marketplace.router, prefix="/api/v1/google-marketplace", tags=["google-marketplace"])
app.include_router(cross_selling.router, prefix="/api/v1/cross-selling", tags=["cross-selling"])
app.include_router(pgrs.router, prefix="/api/v1/pgrs", tags=["pgrs"])

templates_dir = Path(__file__).parent.parent / "templates"
if templates_dir.exists():
    app.mount("/static", StaticFiles(directory=str(templates_dir)), name="static")

setup_a2a_routes(app, settings, base_url="")
