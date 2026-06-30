import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

SYSTEM_PROMPT = """You are an EU AI Act Article 50 compliance specialist.
Deadline: August 2, 2026. Analyze if the company is in scope and
what's needed for compliance:
1. Chatbot/conversational AI disclosure requirements
2. AI-generated content labeling
3. Required technical documentation
Fine: up to EUR 35M or 7% of global annual turnover."""


@router.post("/readiness-check")
async def readiness_check(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    company = data.get("company", "")
    ai_use = data.get("ai_use", "")
    sells_to_eu = data.get("sells_to_eu", "")
    user_prompt = (
        f"Company: {company}\n"
        f"Uses AI for: {ai_use}\n"
        f"Sells to EU: {sells_to_eu}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    return {
        "analysis": response,
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }
