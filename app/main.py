from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import acp_checkout, agents, aws_marketplace, health, subscriptions
from src.config import Settings

settings = Settings()

app = FastAPI(
    title="Engenheiro de Producao AI",
    description="API do sistema multiagente para AEC",
    version="1.0.0",
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
