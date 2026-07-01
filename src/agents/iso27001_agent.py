import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/iso27001", tags=["iso27001"])

SYSTEM_PROMPT = """You are an ISO/IEC 27001:2022 Information Security Management System (ISMS) specialist.
Global standard — recognized in 150+ countries, required by enterprise procurement worldwide.
ISO 27001:2022 updates: 93 controls in 4 themes (Organizational, People, Physical, Technological).
Certification process: Gap analysis → Risk assessment → Controls → Internal audit → Certification audit.
Market: $3.1B global. Required for: government contracts, healthcare, finance, enterprise SaaS.
Provide actionable gap analysis and implementation roadmap."""


@router.post("/gap-analysis")
async def iso27001_gap(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Employees: {data.get('employees', '')}\n"
        f"Current security controls: {data.get('current_controls', 'basic')}\n"
        f"Target: {data.get('target', 'ISO 27001:2022 certification')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "gap_analysis": response,
        "standard": "ISO/IEC 27001:2022",
        "controls": "93 controls across 4 themes",
        "timeline": "9-18 months to certification",
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }


@router.post("/risk-assessment")
async def iso27001_risk(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"ISO 27001 risk assessment for: {data.get('company', '')}\n"
        f"Assets: {data.get('assets', 'data, systems, people')}\n"
        f"Known threats: {data.get('threats', 'cyberattacks, data breaches, insider threats')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"risk_assessment": response}
