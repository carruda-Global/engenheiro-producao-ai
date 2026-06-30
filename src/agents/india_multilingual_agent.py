import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/india", tags=["india_agent"])

SYSTEM_PROMPT_IN = """You are the SallesJam Multilingual Support Agent for India.
Respond in the language the user writes in - English, Hindi, or any regional language.
You help e-commerce and fintech companies automate customer support across
multiple Indian languages, reducing support team costs by 60-80%.
Always offer the activation link when interest is shown."""


@router.post("/chat")
async def chat_india(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    message = data.get("message", "")
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT_IN, message)
    return {
        "response": response,
        "checkout_url": "CRIAR_PRICE_USD_INDIA",
    }
