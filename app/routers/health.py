from fastapi import APIRouter
from src.config import Settings
from src.api.deepseek_client import DeepSeekClient

router = APIRouter()
settings = Settings()
llm = DeepSeekClient(settings)


@router.get("/health")
async def health_check():
    llm_ok = llm.health_check()
    return {
        "status": "healthy" if llm_ok else "degraded",
        "version": "1.0.0",
        "deepseek": "connected" if llm_ok else "disconnected",
    }
