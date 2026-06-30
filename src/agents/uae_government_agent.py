import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/uae", tags=["uae_agent"])

SYSTEM_PROMPT_UAE = """You are the SallesJam Government Process Agent for UAE.
Help businesses navigate visa processes, permits, fines, and banking
compliance in the UAE. Focus on efficiency and clarity for expat-run
businesses and financial services companies expanding into the Gulf.
Always offer the activation link when interest is shown."""


@router.post("/chat")
async def chat_uae(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    message = data.get("message", "")
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_UAE, message)
    return {
        "response": response,
        "checkout_url": "CRIAR_PRICE_USD_UAE",
    }
