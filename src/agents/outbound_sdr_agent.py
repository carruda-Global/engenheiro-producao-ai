import asyncio
import httpx
import logging
import os
import re
from urllib.parse import unquote
from fastapi import APIRouter, BackgroundTasks
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/sdr", tags=["sdr"])
logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_EMAIL_BLOCKLIST = ("example.com", "sentry.io", "wixpress.com", "godaddy.com", "schema.org", "wordpress.com", "noreply", "no-reply", "yourdomain")
_DOMAIN_BLOCKLIST = ("mailings.com.br", "econodata.com.br", "boaempresa.com.br", "99freelas.com.br", "auxilioanet.com.br", "duckduckgo.com", "google.com", "facebook.com", "linkedin.com", "instagram.com", "wikipedia.org")

SECTOR_SEARCH_QUERIES = {
    "construction": ["construtora média porte São Paulo contato comercial email", "construtora contato email construção civil Brasil"],
    "construction_br": ["construtora média porte São Paulo contato comercial email", "construtora contato email construção civil Brasil"],
    "finance": ["fintech company Europe contact email compliance officer", "financial services firm EU contact email DORA"],
    "finance_eu": ["fintech company Europe contact email compliance officer", "financial services firm EU contact email DORA"],
    "tech_saas": ["B2B SaaS startup contact email compliance", "software company United States contact email SOC2"],
    "manufacturing_eu": ["manufacturing company Europe contact email sustainability CSRD", "industrial company EU contact email"],
    "any_eu": ["company Europe contact email AI compliance", "technology company EU contact email EU AI Act"],
}


async def _discover_leads(sector: str, limit: int = 10) -> list[dict]:
    """Descobre leads reais via busca web pública (DuckDuckGo, sem API key) — roda sozinho, sem intervenção manual."""
    queries = SECTOR_SEARCH_QUERIES.get(sector, SECTOR_SEARCH_QUERIES["any_eu"])
    leads: list[dict] = []
    seen_emails: set[str] = set()
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for query in queries:
            if len(leads) >= limit:
                break
            try:
                r = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
                wrapped = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^&"]+)', r.text)
                result_urls = [unquote(u) for u in wrapped][:8]
            except Exception as e:
                logger.warning("[SDR] Search error for '%s': %s", query, e)
                continue

            for url in result_urls:
                if len(leads) >= limit:
                    break
                if any(b in url.lower() for b in _DOMAIN_BLOCKLIST):
                    continue
                try:
                    page = await client.get(url, timeout=8, follow_redirects=True)
                    found = set(EMAIL_RE.findall(page.text))
                    valid = [e for e in found if not any(b in e.lower() for b in _EMAIL_BLOCKLIST)]
                    if valid:
                        company = url.split("//")[-1].split("/")[0].replace("www.", "")
                        email = valid[0]
                        if email not in seen_emails:
                            seen_emails.add(email)
                            leads.append({"company": company, "email": email, "name": ""})
                except Exception:
                    continue
                await asyncio.sleep(1)
    logger.info("[SDR] Discovered %d real leads for sector=%s", len(leads), sector)
    return leads

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
    """Send outbound email campaign via Resend. Se nenhum lead for passado, descobre
    automaticamente via busca web pública — é o que faz o job 24/7 funcionar sozinho."""
    leads = data.get("leads", [])
    sector = data.get("sector", "any_eu")
    limit = data.get("limit", 10)
    background_tasks.add_task(_process_campaign, leads, sector, limit)
    return {"status": "campaign_started", "leads_provided": len(leads), "auto_discover": len(leads) == 0}


async def _process_campaign(leads: list, sector: str, limit: int = 10):
    resend_key = os.getenv("RESEND_API_KEY", "")
    if not resend_key:
        logger.warning("RESEND_API_KEY not set — emails not sent")
        return
    if not leads:
        leads = await _discover_leads(sector, limit)
        if not leads:
            logger.warning("[SDR] Nenhum lead descoberto para sector=%s — pulando ciclo", sector)
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
