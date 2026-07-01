import asyncio
import os
import httpx
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/directories", tags=["directories"])

RESEND_KEY = os.getenv("RESEND_API_KEY", "")

# Diretórios que aceitam submissão via formulário/API — priorizados por tráfego
DIRECTORIES = [
    {"name": "Product Hunt", "url": "https://www.producthunt.com", "type": "manual_once", "traffic": "500k/day", "note": "Launch Tuesday 12:01 AM PST for max votes"},
    {"name": "G2.com", "url": "https://sell.g2.com", "type": "email_request", "traffic": "5M/month", "note": "Free listing, reviews drive enterprise sales"},
    {"name": "Capterra", "url": "https://vendors.capterra.com", "type": "email_request", "traffic": "3M/month", "note": "Pay-per-click after free listing"},
    {"name": "GetApp", "url": "https://www.getapp.com/vendors", "type": "email_request", "traffic": "2M/month", "note": "Gartner property"},
    {"name": "Software Advice", "url": "https://softwareadvice.com/vendors", "type": "email_request", "traffic": "1M/month", "note": "Gartner property"},
    {"name": "SaaSHub", "url": "https://www.saashub.com/submit", "type": "api_submit", "traffic": "500k/month", "note": "Free, auto-approved"},
    {"name": "BetaList", "url": "https://betalist.com/startups/new", "type": "api_submit", "traffic": "100k/month", "note": "Good for early traction"},
    {"name": "AlternativeTo", "url": "https://alternativeto.net/suggest", "type": "api_submit", "traffic": "2M/month", "note": "Gets traffic from OneTrust/Vanta searches"},
    {"name": "SourceForge", "url": "https://sourceforge.net/projects/new", "type": "api_submit", "traffic": "3M/month", "note": "Old but high DA for SEO"},
    {"name": "Trustpilot", "url": "https://businessapp.b2b.trustpilot.com", "type": "email_request", "traffic": "5M/month", "note": "Critical for EU enterprise trust"},
    {"name": "RegTech Analyst", "url": "https://fintech.global/regtech", "type": "email_request", "traffic": "50k/month", "note": "RegTech 100 list organizer"},
    {"name": "OpenPR", "url": "https://www.openpr.com/account", "type": "pr_submit", "traffic": "200k/month", "note": "Free press release distribution"},
    {"name": "EIN Presswire", "url": "https://www.einpresswire.com", "type": "pr_submit", "traffic": "1M/month", "note": "$49/release, indexed by Google News"},
]

LISTING_EMAIL_TEMPLATE = """Subject: Request to List EcoSystem AEC — AI Compliance Platform on {directory}

Hi {directory} Team,

I'd like to list our product, EcoSystem AEC, on {directory}.

Product Details:
- Name: EcoSystem AEC + Regulatory
- Website: https://global-engenharia.com/ecosystem
- Category: RegTech / Compliance Automation / AI Software
- Description: 86 AI agents covering GDPR, LGPD, EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001, NR-1 and more. Used by compliance teams at SMEs and enterprises worldwide.
- Pricing: $149–$999/month, free trial available
- Founded: 2024
- Location: Brazil (global product, EU/US/LATAM markets)

Key differentiators:
• Only platform covering all major 2025-2026 regulatory deadlines in one product
• 86 specialized agents (CSRD, DORA, Whistleblower, M&A Due Diligence, Vendor Risk, etc.)
• Available on Microsoft Marketplace and Google Cloud Marketplace
• Supports 8 languages and 12+ jurisdictions

Happy to provide screenshots, demo video, or any additional information.

Best regards,
Global Match Engenharia
contact@global-engenharia.com
https://global-engenharia.com/ecosystem
"""

PR_TEMPLATE = """FOR IMMEDIATE RELEASE

Brazilian AI Startup Launches 86 Compliance Agents Covering All Major 2025-2026 Regulatory Deadlines

Global Match Engenharia's EcoSystem AEC platform becomes the first solution to address EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001, and NR-1 in a single product

SÃO PAULO, Brazil — July 1, 2026 — Global Match Engenharia today announced the global availability of EcoSystem AEC, an AI-powered compliance platform featuring 86 specialized agents covering the most critical regulatory requirements across Europe, the Americas, and Asia-Pacific.

The platform addresses a critical market gap: as 2025-2026 regulatory deadlines approach — including the EU AI Act (August 2026), CSRD reporting requirements, DORA for financial entities, and Brazil's NR-1 psychosocial risk update — compliance teams are overwhelmed by the volume and complexity of simultaneous requirements.

"We built one agent for every major regulation," said the founding team. "Companies shouldn't need five different vendors to handle GDPR, DORA, CSRD, NIS2, and SOC2 simultaneously."

Key platform capabilities include:
• CSRD reporting assessment for the 50,000 EU companies now required to report
• DORA compliance checks for financial entities (enforcement since January 2025)
• EU AI Act readiness for high-risk AI systems (August 2026 deadline)
• NIS2 scope determination and implementation roadmap
• SOC2 Type II and ISO 27001:2022 gap analysis
• Brazil NR-1 psychosocial risk assessment
• Whistleblower case management (EU Directive 2019/1937)
• M&A due diligence and vendor risk assessment

The platform is available at https://global-engenharia.com/ecosystem starting at $149/month, with enterprise plans available. It is also listed on Microsoft Azure Marketplace and Google Cloud Marketplace.

About Global Match Engenharia
Global Match Engenharia is a Brazilian technology company specializing in AI-powered compliance automation. The company's EcoSystem AEC platform serves compliance teams at SMEs and enterprises across 8 countries.

Contact:
Global Match Engenharia
contact@global-engenharia.com
https://global-engenharia.com/ecosystem

###
"""


async def _send_listing_email(directory: dict) -> bool:
    if not RESEND_KEY:
        return False
    try:
        body = LISTING_EMAIL_TEMPLATE.format(directory=directory["name"])
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "contact@global-engenharia.com",
                    "to": ["carruda2307@gmail.com"],  # send to owner for manual forwarding
                    "subject": f"[AUTO] Listing request draft: {directory['name']}",
                    "text": body,
                },
            )
        return r.status_code < 300
    except Exception as e:
        logger.warning("Directory email error %s: %s", directory["name"], e)
        return False


async def auto_job_directories():
    """Every 72h: sends listing request emails for top directories."""
    await asyncio.sleep(5400)  # 90min warm-up
    batch = 0
    dirs_email = [d for d in DIRECTORIES if d["type"] == "email_request"]
    while True:
        try:
            # Send 2 directory requests per cycle (not to spam)
            start = (batch * 2) % len(dirs_email)
            for d in dirs_email[start:start+2]:
                sent = await _send_listing_email(d)
                logger.info("[CRON] Directory %s: email %s", d["name"], "sent" if sent else "skipped")
                await asyncio.sleep(5)
            batch += 1
        except Exception as e:
            logger.error("[CRON] Directory job error: %s", e)
        await asyncio.sleep(259200)  # 72h


async def auto_job_press_release_distribution():
    """Every 14 days: sends press release to owner email for distribution to OpenPR/EIN."""
    await asyncio.sleep(10800)  # 3h warm-up
    while True:
        try:
            if RESEND_KEY:
                async with httpx.AsyncClient(timeout=15) as client:
                    await client.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                        json={
                            "from": "automacao@global-engenharia.com",
                            "to": ["carruda2307@gmail.com"],
                            "subject": "[AUTO] Press Release pronto — publicar no OpenPR e EIN Presswire",
                            "text": PR_TEMPLATE,
                        },
                    )
                logger.info("[CRON] Press release sent to owner for distribution")
        except Exception as e:
            logger.error("[CRON] PR distribution error: %s", e)
        await asyncio.sleep(1209600)  # 14 dias


@router.get("/list")
async def list_directories():
    return {"directories": DIRECTORIES, "total": len(DIRECTORIES)}

@router.get("/press-release")
async def get_press_release():
    return {"press_release": PR_TEMPLATE}
