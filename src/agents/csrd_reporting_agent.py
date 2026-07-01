import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/csrd", tags=["csrd"])

SYSTEM_PROMPT = """You are a CSRD (Corporate Sustainability Reporting Directive) expert.
EU Directive 2022/2464 — mandatory for companies with 250+ employees or €40M+ revenue.
Deadlines: Large companies FY2024 (report 2025), SMEs FY2026.
Standards: ESRS (European Sustainability Reporting Standards) — E1-E5, S1-S4, G1-G2.
Penalties: Up to 10% of annual revenue + criminal liability for directors.
Analyze the company's readiness and provide a concrete action plan with timelines."""


@router.post("/readiness-check")
async def csrd_readiness(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Employees: {data.get('employees', '')}\n"
        f"Revenue EUR: {data.get('revenue', '')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Current sustainability reporting: {data.get('current_reporting', 'none')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "analysis": response,
        "deadline": "FY2024 report due 2025 (large companies)",
        "standards": "ESRS E1-E5, S1-S4, G1-G2",
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }


@router.post("/gap-analysis")
async def csrd_gap(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Run a CSRD gap analysis for: {data.get('company', '')}\n"
        f"Current ESG practices: {data.get('esg_practices', 'unknown')}\n"
        f"Topics to assess: Climate (E1), Biodiversity (E4), Workforce (S1), Governance (G1)"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"gap_analysis": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}
