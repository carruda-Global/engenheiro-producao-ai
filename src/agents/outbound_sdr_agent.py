import asyncio
import httpx
import logging
import os
from fastapi import APIRouter, BackgroundTasks
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/sdr", tags=["sdr"])
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert B2B cold email copywriter specializing in compliance and AI software.
Write personalized, concise cold emails (max 150 words) that:
- Reference a specific pain point for the company's sector
- Mention the regulatory deadline creating urgency
- Have ONE clear CTA (book a 15-min demo or start free trial)
- Sound human, not like a template
- Subject line under 50 characters, high open rate
Output format: JSON with keys: subject, body, follow_up_d3, follow_up_d7"""

SECTORS = {
    "construction": "NR-1 Psicossocial obrigatória — multa até R$10.000 por empregado",
    "finance": "DORA compliance deadline passed Jan 2025 — penalties up to €10M",
    "tech_saas": "SOC2 Type II required by US enterprise clients — 6 month process",
    "manufacturing_eu": "CSRD reporting mandatory FY2024 — 50,000 companies affected",
    "any_eu": "EU AI Act August 2026 — fines up to €35M or 7% global turnover",
}


@router.post("/generate-email")
async def generate_email(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    company = data.get("company", "")
    sector = data.get("sector", "any_eu")
    contact_name = data.get("contact_name", "")
    pain_point = SECTORS.get(sector, SECTORS["any_eu"])
    prompt = (
        f"Write a cold email for:\n"
        f"Company: {company}\n"
        f"Contact: {contact_name}\n"
        f"Sector: {sector}\n"
        f"Pain point: {pain_point}\n"
        f"Our product: EcoSystem AEC + Regulatory — 71 AI agents that automate compliance\n"
        f"Free trial: global-engenharia.com/ecosystem\n"
        f"Output as JSON: subject, body, follow_up_d3, follow_up_d7"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"email": response, "sector_pain_point": pain_point}


@router.post("/send-campaign")
async def send_campaign(data: dict, background_tasks: BackgroundTasks):
    """Send outbound email campaign via SMTP or Resend API."""
    leads = data.get("leads", [])
    sector = data.get("sector", "any_eu")
    background_tasks.add_task(_process_campaign, leads, sector)
    return {"status": "campaign_started", "leads_queued": len(leads)}


async def _process_campaign(leads: list, sector: str):
    resend_key = os.getenv("RESEND_API_KEY", "")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set — emails not sent")
        return
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    pain_point = SECTORS.get(sector, SECTORS["any_eu"])
    for lead in leads:
        try:
            prompt = (
                f"Company: {lead.get('company', '')}\n"
                f"Contact: {lead.get('name', '')}\n"
                f"Sector: {sector}\n"
                f"Pain: {pain_point}\n"
                f"Product: EcoSystem AEC — 71 AI compliance agents\n"
                f"Trial: global-engenharia.com/ecosystem\n"
                f"Output JSON: subject, body"
            )
            email_json = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {resend_key}"},
                    json={
                        "from": "AION EcoSystem <noreply@global-engenharia.com>",
                        "to": [lead.get("email", "")],
                        "subject": f"[Compliance] {sector} automation",
                        "text": str(email_json),
                    },
                    timeout=10,
                )
            await asyncio.sleep(2)
        except Exception as e:
            logger.error("SDR send error for %s: %s", lead.get("email"), e)


@router.get("/sectors")
async def list_sectors():
    return {"sectors": SECTORS}
